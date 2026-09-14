-- ============================================================
-- BANKING FRAUD, CUSTOMER RISK & PROFITABILITY ANALYTICS
-- PART 2 - SQL ANALYSIS
-- ============================================================

-- ============================================================
-- 1. CREATE DATABASE
-- ============================================================

CREATE DATABASE IF NOT EXISTS banking_analytics;

USE banking_analytics;


-- ============================================================
-- 2. TABLE CREATION
-- ============================================================

DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id VARCHAR(20),
    customer_name VARCHAR(100),
    gender VARCHAR(20),
    age INT,
    city VARCHAR(100),
    state VARCHAR(100),
    customer_segment VARCHAR(50),
    occupation VARCHAR(100),
    annual_income DECIMAL(15,2),
    home_branch_id VARCHAR(20),
    join_date DATE,
    email VARCHAR(150),
    phone VARCHAR(20),
    declared_risk_segment VARCHAR(50)
);


DROP TABLE IF EXISTS accounts;

CREATE TABLE accounts (
    account_id VARCHAR(20),
    customer_id VARCHAR(20),
    account_type VARCHAR(50),
    branch_id VARCHAR(20),
    open_date DATE,
    current_balance DECIMAL(15,2),
    currency VARCHAR(10),
    account_status VARCHAR(50),
    last_activity_date DATE,
    account_tier VARCHAR(50),
    monthly_service_cost DECIMAL(12,2)
);


DROP TABLE IF EXISTS transactions;

CREATE TABLE transactions (
    transaction_id VARCHAR(30),
    account_id VARCHAR(20),
    customer_id VARCHAR(20),
    branch_id VARCHAR(20),
    transaction_datetime DATETIME,
    transaction_type VARCHAR(50),
    transaction_amount DECIMAL(15,2),
    currency VARCHAR(10),
    channel VARCHAR(50),
    merchant_category VARCHAR(100),
    transaction_city VARCHAR(100),
    device_id VARCHAR(50),
    transaction_status VARCHAR(50),
    fee_amount DECIMAL(12,2),
    operational_cost DECIMAL(12,2),
    fraud_confirmed VARCHAR(10),
    high_value_flag INT,
    rapid_transaction_flag INT,
    location_change_flag INT,
    failed_transaction_flag INT,
    basic_fraud_flag_count INT
);


DROP TABLE IF EXISTS loans;

CREATE TABLE loans (
    loan_id VARCHAR(20),
    customer_id VARCHAR(20),
    branch_id VARCHAR(20),
    loan_type VARCHAR(50),
    loan_start_date DATE,
    loan_amount DECIMAL(15,2),
    interest_rate_pct DECIMAL(8,2),
    term_months INT,
    emi_amount DECIMAL(15,2),
    outstanding_balance DECIMAL(15,2),
    loan_status VARCHAR(50),
    default_status VARCHAR(20),
    days_past_due INT
);


DROP TABLE IF EXISTS loan_payments;

CREATE TABLE loan_payments (
    payment_id VARCHAR(30),
    loan_id VARCHAR(20),
    customer_id VARCHAR(20),
    due_date DATE,
    payment_date DATE,
    payment_amount DECIMAL(15,2),
    days_late INT,
    payment_status VARCHAR(50)
);


DROP TABLE IF EXISTS credit_scores;

CREATE TABLE credit_scores (
    credit_score_id VARCHAR(20),
    customer_id VARCHAR(20),
    credit_score INT,
    score_date DATE,
    past_due_accounts INT,
    credit_utilization_pct DECIMAL(8,2),
    hard_inquiries_12m INT,
    credit_history_years INT
);


DROP TABLE IF EXISTS branches;

CREATE TABLE branches (
    branch_id VARCHAR(20),
    branch_name VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(100),
    branch_type VARCHAR(50),
    open_date DATE,
    employee_count INT,
    monthly_operational_cost DECIMAL(15,2)
);


DROP TABLE IF EXISTS complaints;

CREATE TABLE complaints (
    complaint_id VARCHAR(30),
    customer_id VARCHAR(20),
    branch_id VARCHAR(20),
    complaint_date DATE,
    complaint_type VARCHAR(100),
    severity VARCHAR(50),
    complaint_status VARCHAR(50),
    resolved_date DATE,
    service_cost DECIMAL(12,2)
);


DROP TABLE IF EXISTS login_device_activity;

CREATE TABLE login_device_activity (
    login_id VARCHAR(30),
    customer_id VARCHAR(20),
    login_datetime DATETIME,
    device_id VARCHAR(50),
    device_type VARCHAR(50),
    login_city VARCHAR(100),
    ip_address VARCHAR(50),
    login_status VARCHAR(50),
    failed_attempt_count INT
);


-- ============================================================
-- IMPORTANT:
-- IMPORT THE CLEANED CSV FILES USING
-- MYSQL WORKBENCH -> TABLE DATA IMPORT WIZARD
-- ============================================================


-- ============================================================
-- 3. VERIFY IMPORT
-- ============================================================

SELECT COUNT(*) AS customers_count
FROM customers;

SELECT COUNT(*) AS accounts_count
FROM accounts;

SELECT COUNT(*) AS transactions_count
FROM transactions;

SELECT COUNT(*) AS loans_count
FROM loans;

SELECT COUNT(*) AS loan_payments_count
FROM loan_payments;

SELECT COUNT(*) AS credit_scores_count
FROM credit_scores;

SELECT COUNT(*) AS branches_count
FROM branches;

SELECT COUNT(*) AS complaints_count
FROM complaints;

SELECT COUNT(*) AS login_activity_count
FROM login_device_activity;


-- ============================================================
-- 4. DAILY TRANSACTION VOLUME
-- ============================================================

SELECT
    DATE(transaction_datetime) AS transaction_date,
    COUNT(*) AS transaction_volume
FROM transactions
GROUP BY DATE(transaction_datetime)
ORDER BY transaction_date;


-- ============================================================
-- 5. MONTHLY TRANSACTION VALUE
-- ============================================================

SELECT
    DATE_FORMAT(transaction_datetime, '%Y-%m') AS transaction_month,
    COUNT(*) AS total_transactions,
    ROUND(SUM(transaction_amount), 2) AS total_transaction_value
FROM transactions
WHERE transaction_status = 'Success'
GROUP BY DATE_FORMAT(transaction_datetime, '%Y-%m')
ORDER BY transaction_month;


-- ============================================================
-- 6. AVERAGE TRANSACTION AMOUNT
-- ============================================================

SELECT
    ROUND(AVG(transaction_amount), 2) AS average_transaction_amount
FROM transactions
WHERE transaction_status = 'Success';


-- ============================================================
-- 7. CUSTOMER LIFETIME TRANSACTION VALUE
-- ============================================================

SELECT
    c.customer_id,
    c.customer_name,
    COUNT(t.transaction_id) AS total_transactions,
    ROUND(SUM(t.transaction_amount), 2) AS lifetime_transaction_value
FROM customers c
JOIN transactions t
    ON c.customer_id = t.customer_id
WHERE t.transaction_status = 'Success'
GROUP BY
    c.customer_id,
    c.customer_name
ORDER BY lifetime_transaction_value DESC;


-- ============================================================
-- 8. TOP CUSTOMERS BY ACCOUNT BALANCE
-- ============================================================

SELECT
    c.customer_id,
    c.customer_name,
    COUNT(a.account_id) AS total_accounts,
    ROUND(SUM(a.current_balance), 2) AS total_balance
FROM customers c
JOIN accounts a
    ON c.customer_id = a.customer_id
GROUP BY
    c.customer_id,
    c.customer_name
ORDER BY total_balance DESC
LIMIT 10;


-- ============================================================
-- 9. TOP BRANCHES BY REVENUE
-- Transaction fees are treated as transaction revenue here.
-- ============================================================

SELECT
    b.branch_id,
    b.branch_name,
    b.city,
    ROUND(SUM(t.fee_amount), 2) AS transaction_fee_revenue
FROM branches b
JOIN transactions t
    ON b.branch_id = t.branch_id
WHERE t.transaction_status = 'Success'
GROUP BY
    b.branch_id,
    b.branch_name,
    b.city
ORDER BY transaction_fee_revenue DESC;


-- ============================================================
-- 10. LOAN DEFAULT RATE
-- ============================================================

SELECT
    COUNT(*) AS total_loans,

    SUM(
        CASE
            WHEN default_status = 'Yes'
            THEN 1
            ELSE 0
        END
    ) AS defaulted_loans,

    ROUND(
        SUM(
            CASE
                WHEN default_status = 'Yes'
                THEN 1
                ELSE 0
            END
        ) * 100.0 / COUNT(*),
        2
    ) AS default_rate_pct

FROM loans;


-- ============================================================
-- 11. CUSTOMER REPAYMENT RATE
-- ============================================================

SELECT
    customer_id,

    COUNT(*) AS total_payment_records,

    SUM(
        CASE
            WHEN payment_status = 'Paid'
            THEN 1
            ELSE 0
        END
    ) AS successful_payments,

    ROUND(
        SUM(
            CASE
                WHEN payment_status = 'Paid'
                THEN 1
                ELSE 0
            END
        ) * 100.0
        / COUNT(*),
        2
    ) AS repayment_rate_pct

FROM loan_payments

GROUP BY customer_id

ORDER BY repayment_rate_pct DESC;


-- ============================================================
-- 12. DORMANT ACCOUNTS
-- ============================================================

SELECT
    a.account_id,
    a.customer_id,
    c.customer_name,
    a.account_type,
    a.current_balance,
    a.last_activity_date,
    a.account_status
FROM accounts a

LEFT JOIN customers c
    ON a.customer_id = c.customer_id

WHERE a.account_status = 'Dormant'

ORDER BY a.last_activity_date;


-- ============================================================
-- 13. CUSTOMERS WITH MULTIPLE ACCOUNTS
-- ============================================================

SELECT
    c.customer_id,
    c.customer_name,
    COUNT(a.account_id) AS number_of_accounts
FROM customers c

JOIN accounts a
    ON c.customer_id = a.customer_id

GROUP BY
    c.customer_id,
    c.customer_name

HAVING COUNT(a.account_id) > 1

ORDER BY number_of_accounts DESC;


-- ============================================================
-- 14. CUSTOMERS WITH UNUSUAL TRANSACTION FREQUENCY
-- ============================================================

WITH customer_transaction_frequency AS (

    SELECT
        customer_id,
        COUNT(*) AS transaction_count
    FROM transactions
    GROUP BY customer_id

),

average_frequency AS (

    SELECT
        AVG(transaction_count) AS avg_transaction_count
    FROM customer_transaction_frequency

)

SELECT
    ctf.customer_id,
    c.customer_name,
    ctf.transaction_count,
    ROUND(af.avg_transaction_count, 2) AS average_transaction_count

FROM customer_transaction_frequency ctf

JOIN customers c
    ON ctf.customer_id = c.customer_id

CROSS JOIN average_frequency af

WHERE ctf.transaction_count >
      af.avg_transaction_count * 1.5

ORDER BY ctf.transaction_count DESC;


-- ============================================================
-- 15. RUNNING TRANSACTION TOTAL
-- WINDOW FUNCTION
-- ============================================================

SELECT
    transaction_id,
    customer_id,
    transaction_datetime,
    transaction_amount,

    ROUND(
        SUM(transaction_amount)
        OVER (
            PARTITION BY customer_id
            ORDER BY transaction_datetime, transaction_id
            ROWS BETWEEN UNBOUNDED PRECEDING
            AND CURRENT ROW
        ),
        2
    ) AS running_transaction_total

FROM transactions

WHERE transaction_status = 'Success'

ORDER BY
    customer_id,
    transaction_datetime;


-- ============================================================
-- 16. MONTH-OVER-MONTH TRANSACTION GROWTH
-- CTE + LAG WINDOW FUNCTION
-- ============================================================

WITH monthly_transactions AS (

    SELECT
        DATE_FORMAT(
            transaction_datetime,
            '%Y-%m'
        ) AS transaction_month,

        SUM(transaction_amount) AS monthly_value

    FROM transactions

    WHERE transaction_status = 'Success'

    GROUP BY
        DATE_FORMAT(
            transaction_datetime,
            '%Y-%m'
        )

),

monthly_growth AS (

    SELECT
        transaction_month,
        monthly_value,

        LAG(monthly_value)
        OVER (
            ORDER BY transaction_month
        ) AS previous_month_value

    FROM monthly_transactions

)

SELECT
    transaction_month,

    ROUND(
        monthly_value,
        2
    ) AS monthly_value,

    ROUND(
        previous_month_value,
        2
    ) AS previous_month_value,

    ROUND(
        (
            monthly_value - previous_month_value
        )
        / NULLIF(previous_month_value, 0)
        * 100,
        2
    ) AS month_over_month_growth_pct

FROM monthly_growth

ORDER BY transaction_month;


-- ============================================================
-- 17. BRANCH RANKING
-- ============================================================

WITH branch_performance AS (

    SELECT
        b.branch_id,
        b.branch_name,

        COUNT(t.transaction_id) AS total_transactions,

        SUM(t.transaction_amount) AS transaction_value,

        SUM(t.fee_amount) AS fee_revenue

    FROM branches b

    LEFT JOIN transactions t
        ON b.branch_id = t.branch_id
        AND t.transaction_status = 'Success'

    GROUP BY
        b.branch_id,
        b.branch_name

)

SELECT
    branch_id,
    branch_name,
    total_transactions,

    ROUND(
        transaction_value,
        2
    ) AS transaction_value,

    ROUND(
        fee_revenue,
        2
    ) AS fee_revenue,

    DENSE_RANK()
    OVER (
        ORDER BY fee_revenue DESC
    ) AS branch_rank

FROM branch_performance

ORDER BY branch_rank;


-- ============================================================
-- 18. CUSTOMER RANKING
-- ============================================================

WITH customer_value AS (

    SELECT
        c.customer_id,
        c.customer_name,

        COUNT(t.transaction_id) AS transaction_count,

        COALESCE(
            SUM(t.transaction_amount),
            0
        ) AS total_transaction_value

    FROM customers c

    LEFT JOIN transactions t
        ON c.customer_id = t.customer_id
        AND t.transaction_status = 'Success'

    GROUP BY
        c.customer_id,
        c.customer_name

)

SELECT
    customer_id,
    customer_name,
    transaction_count,

    ROUND(
        total_transaction_value,
        2
    ) AS total_transaction_value,

    DENSE_RANK()
    OVER (
        ORDER BY total_transaction_value DESC
    ) AS customer_rank

FROM customer_value

ORDER BY customer_rank;


-- ============================================================
-- 19. JOIN ANALYSIS
-- CUSTOMER + ACCOUNT + BRANCH
-- ============================================================

SELECT
    c.customer_id,
    c.customer_name,
    c.customer_segment,

    a.account_id,
    a.account_type,
    a.current_balance,

    b.branch_name,
    b.city AS branch_city

FROM customers c

JOIN accounts a
    ON c.customer_id = a.customer_id

LEFT JOIN branches b
    ON a.branch_id = b.branch_id

ORDER BY c.customer_id;


-- ============================================================
-- 20. SUBQUERY
-- CUSTOMERS ABOVE AVERAGE ACCOUNT BALANCE
-- ============================================================

SELECT
    c.customer_id,
    c.customer_name,
    a.current_balance

FROM customers c

JOIN accounts a
    ON c.customer_id = a.customer_id

WHERE a.current_balance >
(
    SELECT AVG(current_balance)
    FROM accounts
)

ORDER BY a.current_balance DESC;


-- ============================================================
-- 21. CASE WHEN
-- CUSTOMER BALANCE CATEGORY
-- ============================================================

SELECT
    c.customer_id,
    c.customer_name,

    ROUND(
        SUM(a.current_balance),
        2
    ) AS total_balance,

    CASE

        WHEN SUM(a.current_balance) >= 1000000
        THEN 'High Value'

        WHEN SUM(a.current_balance) >= 500000
        THEN 'Medium Value'

        ELSE 'Low Value'

    END AS customer_value_segment

FROM customers c

JOIN accounts a
    ON c.customer_id = a.customer_id

GROUP BY
    c.customer_id,
    c.customer_name

ORDER BY total_balance DESC;


-- ============================================================
-- 22. CTE
-- HIGH VALUE CUSTOMERS
-- ============================================================

WITH high_value_customers AS (

    SELECT
        customer_id,
        SUM(transaction_amount) AS transaction_value

    FROM transactions

    WHERE transaction_status = 'Success'

    GROUP BY customer_id

)

SELECT
    h.customer_id,
    c.customer_name,

    ROUND(
        h.transaction_value,
        2
    ) AS transaction_value

FROM high_value_customers h

JOIN customers c
    ON h.customer_id = c.customer_id

WHERE h.transaction_value >
(
    SELECT AVG(transaction_value)
    FROM high_value_customers
)

ORDER BY transaction_value DESC;


-- ============================================================
-- 23. FRAUD FLAG SUMMARY
-- ============================================================

SELECT
    basic_fraud_flag_count,
    COUNT(*) AS transaction_count,
    ROUND(SUM(transaction_amount), 2) AS transaction_value
FROM transactions
GROUP BY basic_fraud_flag_count
ORDER BY basic_fraud_flag_count;


-- ============================================================
-- 24. SUSPICIOUS TRANSACTIONS
-- ============================================================

SELECT
    transaction_id,
    customer_id,
    account_id,
    transaction_datetime,
    transaction_amount,
    transaction_city,
    transaction_status,

    high_value_flag,
    rapid_transaction_flag,
    location_change_flag,
    failed_transaction_flag,

    basic_fraud_flag_count

FROM transactions

WHERE basic_fraud_flag_count >= 2

ORDER BY
    basic_fraud_flag_count DESC,
    transaction_amount DESC;


-- ============================================================
-- 25. FRAUD BY BRANCH
-- ============================================================

SELECT
    b.branch_id,
    b.branch_name,

    COUNT(
        CASE
            WHEN t.basic_fraud_flag_count >= 2
            THEN 1
        END
    ) AS suspicious_transactions,

    ROUND(
        SUM(
            CASE
                WHEN t.basic_fraud_flag_count >= 2
                THEN t.transaction_amount
                ELSE 0
            END
        ),
        2
    ) AS suspicious_transaction_value

FROM branches b

LEFT JOIN transactions t
    ON b.branch_id = t.branch_id

GROUP BY
    b.branch_id,
    b.branch_name

ORDER BY suspicious_transactions DESC;


-- ============================================================
-- 26. CUSTOMER LOAN RISK
-- ============================================================

SELECT
    c.customer_id,
    c.customer_name,

    cs.credit_score,

    l.loan_amount,
    l.outstanding_balance,
    l.days_past_due,
    l.default_status,

    CASE

        WHEN cs.credit_score < 550
             OR l.days_past_due > 60
             OR l.default_status = 'Yes'
        THEN 'High Risk'

        WHEN cs.credit_score < 650
             OR l.days_past_due > 30
        THEN 'Medium Risk'

        ELSE 'Low Risk'

    END AS loan_risk_segment

FROM customers c

JOIN loans l
    ON c.customer_id = l.customer_id

LEFT JOIN credit_scores cs
    ON c.customer_id = cs.customer_id

ORDER BY
    l.days_past_due DESC,
    cs.credit_score ASC;


-- ============================================================
-- 27. VIEW - CUSTOMER TRANSACTION SUMMARY
-- ============================================================

DROP VIEW IF EXISTS customer_transaction_summary;

CREATE VIEW customer_transaction_summary AS

SELECT
    c.customer_id,
    c.customer_name,
    c.customer_segment,

    COUNT(t.transaction_id) AS total_transactions,

    COALESCE(
        SUM(t.transaction_amount),
        0
    ) AS total_transaction_value,

    COALESCE(
        AVG(t.transaction_amount),
        0
    ) AS average_transaction_value

FROM customers c

LEFT JOIN transactions t
    ON c.customer_id = t.customer_id

GROUP BY
    c.customer_id,
    c.customer_name,
    c.customer_segment;


SELECT *
FROM customer_transaction_summary
ORDER BY total_transaction_value DESC;


-- ============================================================
-- 28. VIEW - LOAN RISK SUMMARY
-- ============================================================

DROP VIEW IF EXISTS loan_risk_summary;

CREATE VIEW loan_risk_summary AS

SELECT
    l.loan_id,
    l.customer_id,
    l.branch_id,

    l.loan_amount,
    l.outstanding_balance,
    l.days_past_due,
    l.default_status,

    cs.credit_score,

    CASE

        WHEN cs.credit_score < 550
             OR l.default_status = 'Yes'
             OR l.days_past_due > 60
        THEN 'High Risk'

        WHEN cs.credit_score < 650
             OR l.days_past_due > 30
        THEN 'Medium Risk'

        ELSE 'Low Risk'

    END AS risk_segment

FROM loans l

LEFT JOIN credit_scores cs
    ON l.customer_id = cs.customer_id;


SELECT *
FROM loan_risk_summary;


-- ============================================================
-- 29. INDEXES
-- ============================================================

CREATE INDEX idx_customers_customer_id
ON customers(customer_id);

CREATE INDEX idx_accounts_customer_id
ON accounts(customer_id);

CREATE INDEX idx_accounts_branch_id
ON accounts(branch_id);

CREATE INDEX idx_transactions_customer_id
ON transactions(customer_id);

CREATE INDEX idx_transactions_account_id
ON transactions(account_id);

CREATE INDEX idx_transactions_branch_id
ON transactions(branch_id);

CREATE INDEX idx_transactions_datetime
ON transactions(transaction_datetime);

CREATE INDEX idx_loans_customer_id
ON loans(customer_id);

CREATE INDEX idx_loans_branch_id
ON loans(branch_id);

CREATE INDEX idx_payments_customer_id
ON loan_payments(customer_id);

CREATE INDEX idx_credit_customer_id
ON credit_scores(customer_id);


-- ============================================================
-- PART 2 COMPLETE
-- ============================================================

SELECT
    'PART 2 - SQL ANALYSIS COMPLETED SUCCESSFULLY'
    AS status;