# Banking Fraud, Customer Risk & Profitability Analytics

An end-to-end banking analytics project using **Python, MySQL, Statistics, and Power BI** to analyze fraud risk, loan defaults, customer profitability, transaction behavior, and banking performance.

---

## Project Overview

A retail bank is experiencing an increase in:

- Suspicious transactions
- Loan defaults
- Customer complaints
- Operational costs
- High-risk customer activity

The objective of this project is to analyze banking data and identify:

- Fraudulent and suspicious transactions
- High-risk customers
- High-risk loans
- Loan default patterns
- Profitable and loss-making customers
- High-value and high-risk customers
- Branch-level risk
- Statistical relationships between credit score and loan default

---

## Tools & Technologies

- Python
- Pandas
- NumPy
- SciPy
- MySQL
- SQL
- Power BI
- DAX
- Statistics
- Excel / CSV

---

# Power BI Dashboards

## Executive Dashboard

The Executive Dashboard provides an overall view of banking performance, including customers, transactions, loan portfolio, defaults, fraud exposure, and customer profitability.

![Executive Dashboard](Power%20Bi/Dashboards%20Screenshots/Executive%20Dashboard.png)

---

## Fraud Analysis Dashboard

The Fraud Analysis Dashboard focuses on suspicious transactions, fraud risk scores, branch-level fraud activity, and customer risk segments.

![Fraud Analysis Dashboard](Power%20Bi/Dashboards%20Screenshots/Fraud%20Analysis.png)

---

## Loan Risk Analysis Dashboard

The Loan Risk Dashboard analyzes loan portfolio performance, credit score distribution, loan risk segments, default rates, and branch-level loan risk.

![Loan Analysis Dashboard](Power%20Bi/Dashboards%20Screenshots/Loan%20Analysis.png)

---

# Project Structure

```text
Banking Fraud Project
│
├── Rawdata
│   ├── customers.csv
│   ├── accounts.csv
│   ├── transactions.csv
│   ├── loans.csv
│   ├── loan_payments.csv
│   ├── credit_scores.csv
│   ├── branches.csv
│   ├── complaints.csv
│   └── login_device_activity.csv
│
├── Cleaned Data
│   ├── customers_cleaned.csv
│   ├── accounts_cleaned.csv
│   ├── transactions_cleaned.csv
│   ├── loans_cleaned.csv
│   ├── loan_payments_cleaned.csv
│   ├── credit_scores_cleaned.csv
│   ├── branches_cleaned.csv
│   ├── complaints_cleaned.csv
│   └── login_device_activity_cleaned.csv
│
├── Data Quality report
│   ├── duplicate_customers_report.csv
│   ├── invalid_transactions_report.csv
│   ├── invalid_transaction_account_relationships.csv
│   ├── invalid_transaction_dates.csv
│   ├── invalid_login_dates.csv
│   ├── invalid_account_customer_relationships.csv
│   ├── invalid_account_branch_relationships.csv
│   ├── transaction_customer_mismatch_report.csv
│   ├── high_value_transactions.csv
│   ├── rapid_transactions.csv
│   ├── sudden_location_changes.csv
│   ├── repeated_failed_transaction_customers.csv
│   ├── multiple_transaction_device_customers.csv
│   ├── multiple_login_device_customers.csv
│   └── high_failed_login_attempts.csv
│
├── Python Analysis
│   ├── Data Preparation.py
│   ├── Fraud Investigation.py
│   ├── Loan Risk Analysis.py
│   ├── Customer Profitability Analysis.py
│   └── Statistical Analysis.py
│
├── SQL
│   └── banking_analysis.sql
│
├── Fraud Analysis
│
├── Loan Risk Analysis
│
├── Customer Profitability
│
├── Statistical Analysis
│
├── Power Bi
│   ├── Banking Analytics.pbix
│   └── Dashboards Screenshots
│       ├── Executive Dashboard.png
│       ├── Fraud Analysis.png
│       └── Loan Analysis.png
│
├── Report
│   └── Banking_Fraud_Customer_Risk_Profitability_Report.pdf
│
└── README.md
