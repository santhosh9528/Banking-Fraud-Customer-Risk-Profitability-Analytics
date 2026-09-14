import pandas as pd
import numpy as np
import os

# ============================================================
# BANKING FRAUD, CUSTOMER RISK & PROFITABILITY ANALYTICS
# PART 5 - CUSTOMER PROFITABILITY ANALYSIS
# ============================================================

print("=" * 90)
print("PART 5 - CUSTOMER PROFITABILITY ANALYSIS")
print("=" * 90)

# ============================================================
# 1. PATHS
# ============================================================

cleaned_path = r"C:\Users\Hooooo\Documents\Excel\Banking Fraud Project\Cleaned Data"

fraud_path = r"C:\Users\Hooooo\Documents\Excel\Banking Fraud Project\Fraud Analysis"

loan_risk_path = r"C:\Users\Hooooo\Documents\Excel\Banking Fraud Project\Loan Risk Analysis"

output_path = r"C:\Users\Hooooo\Documents\Excel\Banking Fraud Project\Customer Profitability"

os.makedirs(output_path, exist_ok=True)

print("\nCleaned Data Path:")
print(cleaned_path)

print("\nOutput Path:")
print(output_path)

# ============================================================
# 2. LOAD DATASETS
# ============================================================

customers = pd.read_csv(
    os.path.join(cleaned_path, "customers_cleaned.csv")
)

accounts = pd.read_csv(
    os.path.join(cleaned_path, "accounts_cleaned.csv")
)

transactions = pd.read_csv(
    os.path.join(cleaned_path, "transactions_cleaned.csv")
)

loans = pd.read_csv(
    os.path.join(cleaned_path, "loans_cleaned.csv")
)

loan_payments = pd.read_csv(
    os.path.join(cleaned_path, "loan_payments_cleaned.csv")
)

complaints = pd.read_csv(
    os.path.join(cleaned_path, "complaints_cleaned.csv")
)

fraud_summary = pd.read_csv(
    os.path.join(
        fraud_path,
        "customer_fraud_risk_summary.csv"
    )
)

loan_risk_summary = pd.read_csv(
    os.path.join(
        loan_risk_path,
        "customer_loan_risk_summary.csv"
    )
)

print("\nDatasets loaded successfully!")

print("Customers:", customers.shape)
print("Accounts:", accounts.shape)
print("Transactions:", transactions.shape)
print("Loans:", loans.shape)
print("Loan Payments:", loan_payments.shape)
print("Complaints:", complaints.shape)
print("Fraud Summary:", fraud_summary.shape)
print("Loan Risk Summary:", loan_risk_summary.shape)

# ============================================================
# 3. BASIC STANDARDIZATION
# ============================================================

transactions["transaction_status"] = (
    transactions["transaction_status"]
    .astype(str)
    .str.strip()
    .str.title()
)

loans["default_status"] = (
    loans["default_status"]
    .astype(str)
    .str.strip()
    .str.title()
)

loan_payments["payment_status"] = (
    loan_payments["payment_status"]
    .astype(str)
    .str.strip()
    .str.title()
)

customers["customer_segment"] = (
    customers["customer_segment"]
    .astype(str)
    .str.strip()
    .str.title()
)

# ============================================================
# 4. VALID CUSTOMER IDS
# ============================================================

valid_customer_ids = set(
    customers["customer_id"].dropna()
)

# ============================================================
# 5. TRANSACTION REVENUE & COST
# ============================================================

print("\n" + "=" * 90)
print("1. TRANSACTION REVENUE AND COST")
print("=" * 90)

transactions_analysis = transactions[
    transactions["customer_id"].isin(valid_customer_ids)
].copy()

transaction_profitability = (
    transactions_analysis
    .groupby("customer_id")
    .agg(
        total_transactions=(
            "transaction_id",
            "count"
        ),

        total_transaction_value=(
            "transaction_amount",
            "sum"
        ),

        transaction_fee_revenue=(
            "fee_amount",
            "sum"
        ),

        transaction_operational_cost=(
            "operational_cost",
            "sum"
        )
    )
    .reset_index()
)

transaction_profitability[
    "net_transaction_profit"
] = (
    transaction_profitability[
        "transaction_fee_revenue"
    ]
    -
    transaction_profitability[
        "transaction_operational_cost"
    ]
)

print("\nTransaction Profitability Sample:")
print(transaction_profitability.head(20))

# ============================================================
# 6. ACCOUNT BALANCE & SERVICE COST
# ============================================================

print("\n" + "=" * 90)
print("2. ACCOUNT BALANCE AND SERVICE COST")
print("=" * 90)

accounts_analysis = accounts[
    accounts["customer_id"].isin(valid_customer_ids)
].copy()

account_summary = (
    accounts_analysis
    .groupby("customer_id")
    .agg(
        number_of_accounts=(
            "account_id",
            "nunique"
        ),

        total_account_balance=(
            "current_balance",
            "sum"
        ),

        monthly_account_service_cost=(
            "monthly_service_cost",
            "sum"
        )
    )
    .reset_index()
)

# Annualize monthly account service cost
account_summary[
    "annual_account_service_cost"
] = (
    account_summary[
        "monthly_account_service_cost"
    ] * 12
)

print("\nAccount Summary Sample:")
print(account_summary.head(20))

# ============================================================
# 7. COMPLAINT SERVICE COST
# ============================================================

print("\n" + "=" * 90)
print("3. COMPLAINT SERVICE COST")
print("=" * 90)

complaints_analysis = complaints[
    complaints["customer_id"].isin(valid_customer_ids)
].copy()

complaint_summary = (
    complaints_analysis
    .groupby("customer_id")
    .agg(
        total_complaints=(
            "complaint_id",
            "count"
        ),

        complaint_service_cost=(
            "service_cost",
            "sum"
        )
    )
    .reset_index()
)

print("\nComplaint Summary Sample:")
print(complaint_summary.head(20))

# ============================================================
# 8. LOAN INTEREST REVENUE
# ============================================================

print("\n" + "=" * 90)
print("4. LOAN INTEREST REVENUE")
print("=" * 90)

loans_analysis = loans[
    loans["customer_id"].isin(valid_customer_ids)
    &
    (loans["loan_amount"] > 0)
    &
    (loans["interest_rate_pct"] >= 0)
].copy()

# Estimated annual interest revenue based on outstanding balance
loans_analysis[
    "estimated_annual_interest_revenue"
] = (
    loans_analysis["outstanding_balance"]
    *
    (
        loans_analysis["interest_rate_pct"] / 100
    )
)

loan_profitability = (
    loans_analysis
    .groupby("customer_id")
    .agg(
        total_loans=(
            "loan_id",
            "count"
        ),

        total_loan_amount=(
            "loan_amount",
            "sum"
        ),

        total_outstanding_balance=(
            "outstanding_balance",
            "sum"
        ),

        estimated_interest_revenue=(
            "estimated_annual_interest_revenue",
            "sum"
        ),

        defaulted_loans=(
            "default_status",
            lambda x: (x == "Yes").sum()
        )
    )
    .reset_index()
)

print("\nLoan Revenue Sample:")
print(loan_profitability.head(20))

# ============================================================
# 9. LOAN REPAYMENT SUMMARY
# ============================================================

print("\n" + "=" * 90)
print("5. LOAN REPAYMENT SUMMARY")
print("=" * 90)

loan_payments_analysis = loan_payments[
    loan_payments["customer_id"].isin(
        valid_customer_ids
    )
    &
    (loan_payments["payment_amount"] > 0)
].copy()

repayment_summary = (
    loan_payments_analysis
    .groupby("customer_id")
    .agg(
        total_payments_made=(
            "payment_amount",
            "sum"
        ),

        payment_records=(
            "payment_id",
            "count"
        ),

        delayed_payment_records=(
            "days_late",
            lambda x: (x > 0).sum()
        ),

        max_days_late=(
            "days_late",
            "max"
        )
    )
    .reset_index()
)

print("\nRepayment Summary Sample:")
print(repayment_summary.head(20))

# ============================================================
# 10. CREATE CUSTOMER MASTER PROFITABILITY TABLE
# ============================================================

print("\n" + "=" * 90)
print("6. BUILD CUSTOMER PROFITABILITY MASTER")
print("=" * 90)

customer_profitability = customers[
    [
        "customer_id",
        "customer_name",
        "customer_segment",
        "city",
        "state",
        "annual_income",
        "declared_risk_segment"
    ]
].copy()

customer_profitability = pd.merge(
    customer_profitability,
    transaction_profitability,
    on="customer_id",
    how="left"
)

customer_profitability = pd.merge(
    customer_profitability,
    account_summary,
    on="customer_id",
    how="left"
)

customer_profitability = pd.merge(
    customer_profitability,
    complaint_summary,
    on="customer_id",
    how="left"
)

customer_profitability = pd.merge(
    customer_profitability,
    loan_profitability,
    on="customer_id",
    how="left"
)

customer_profitability = pd.merge(
    customer_profitability,
    repayment_summary,
    on="customer_id",
    how="left"
)

# ============================================================
# 11. MERGE FRAUD RISK
# ============================================================

fraud_cols = [
    "customer_id",
    "suspicious_transactions",
    "max_fraud_risk_score",
    "confirmed_fraud_transactions",
    "customer_fraud_risk_level"
]

available_fraud_cols = [
    col for col in fraud_cols
    if col in fraud_summary.columns
]

customer_profitability = pd.merge(
    customer_profitability,
    fraud_summary[available_fraud_cols],
    on="customer_id",
    how="left"
)

# ============================================================
# 12. MERGE LOAN RISK
# ============================================================

loan_risk_cols = [
    "customer_id",
    "max_loan_risk_score",
    "average_loan_risk_score",
    "customer_loan_risk_level"
]

available_loan_risk_cols = [
    col for col in loan_risk_cols
    if col in loan_risk_summary.columns
]

customer_profitability = pd.merge(
    customer_profitability,
    loan_risk_summary[available_loan_risk_cols],
    on="customer_id",
    how="left"
)

# ============================================================
# 13. FILL MISSING NUMERIC VALUES
# ============================================================

numeric_cols = [
    "total_transactions",
    "total_transaction_value",
    "transaction_fee_revenue",
    "transaction_operational_cost",
    "net_transaction_profit",
    "number_of_accounts",
    "total_account_balance",
    "monthly_account_service_cost",
    "annual_account_service_cost",
    "total_complaints",
    "complaint_service_cost",
    "total_loans",
    "total_loan_amount",
    "total_outstanding_balance",
    "estimated_interest_revenue",
    "defaulted_loans",
    "total_payments_made",
    "payment_records",
    "delayed_payment_records",
    "max_days_late",
    "suspicious_transactions",
    "max_fraud_risk_score",
    "confirmed_fraud_transactions",
    "max_loan_risk_score",
    "average_loan_risk_score"
]

for col in numeric_cols:
    if col in customer_profitability.columns:
        customer_profitability[col] = (
            customer_profitability[col]
            .fillna(0)
        )

# ============================================================
# 14. CALCULATE TOTAL REVENUE
# ============================================================

print("\n" + "=" * 90)
print("7. CALCULATE CUSTOMER REVENUE")
print("=" * 90)

customer_profitability[
    "customer_revenue"
] = (
    customer_profitability[
        "transaction_fee_revenue"
    ]
    +
    customer_profitability[
        "estimated_interest_revenue"
    ]
)

# ============================================================
# 15. CALCULATE TOTAL COST
# ============================================================

customer_profitability[
    "customer_operational_cost"
] = (
    customer_profitability[
        "transaction_operational_cost"
    ]
    +
    customer_profitability[
        "annual_account_service_cost"
    ]
    +
    customer_profitability[
        "complaint_service_cost"
    ]
)

# ============================================================
# 16. CUSTOMER PROFIT
# ============================================================

customer_profitability[
    "customer_profit"
] = (
    customer_profitability[
        "customer_revenue"
    ]
    -
    customer_profitability[
        "customer_operational_cost"
    ]
)

customer_profitability[
    "profit_margin_pct"
] = np.where(
    customer_profitability[
        "customer_revenue"
    ] > 0,

    customer_profitability[
        "customer_profit"
    ]
    /
    customer_profitability[
        "customer_revenue"
    ]
    * 100,

    0
)

print("\nCustomer Profitability Sample:")

print(
    customer_profitability[
        [
            "customer_id",
            "customer_name",
            "customer_revenue",
            "customer_operational_cost",
            "customer_profit",
            "profit_margin_pct"
        ]
    ].head(20)
)

# ============================================================
# 17. PROFITABILITY SEGMENT
# ============================================================

print("\n" + "=" * 90)
print("8. PROFITABILITY SEGMENTS")
print("=" * 90)

profit_median = customer_profitability[
    "customer_profit"
].median()

profit_q75 = customer_profitability[
    "customer_profit"
].quantile(0.75)

customer_profitability[
    "profitability_segment"
] = np.select(
    [
        customer_profitability[
            "customer_profit"
        ] < 0,

        customer_profitability[
            "customer_profit"
        ] >= profit_q75,

        customer_profitability[
            "customer_profit"
        ] >= profit_median
    ],
    [
        "Loss Making",
        "High Profit",
        "Medium Profit"
    ],
    default="Low Profit"
)

print(
    customer_profitability[
        "profitability_segment"
    ].value_counts()
)

# ============================================================
# 18. MOST PROFITABLE CUSTOMERS
# ============================================================

print("\n" + "=" * 90)
print("9. MOST PROFITABLE CUSTOMERS")
print("=" * 90)

most_profitable_customers = (
    customer_profitability
    .sort_values(
        "customer_profit",
        ascending=False
    )
    .head(25)
    .copy()
)

print(
    most_profitable_customers[
        [
            "customer_id",
            "customer_name",
            "customer_segment",
            "customer_revenue",
            "customer_operational_cost",
            "customer_profit",
            "profit_margin_pct"
        ]
    ]
)

# ============================================================
# 19. LOSS-MAKING CUSTOMERS
# ============================================================

print("\n" + "=" * 90)
print("10. LOSS-MAKING CUSTOMERS")
print("=" * 90)

loss_making_customers = (
    customer_profitability[
        customer_profitability[
            "customer_profit"
        ] < 0
    ]
    .sort_values(
        "customer_profit",
        ascending=True
    )
    .copy()
)

print(
    "Loss-Making Customers:",
    len(loss_making_customers)
)

print(
    loss_making_customers[
        [
            "customer_id",
            "customer_name",
            "customer_revenue",
            "customer_operational_cost",
            "customer_profit"
        ]
    ].head(25)
)

# ============================================================
# 20. HIGH-VALUE CUSTOMER DEFINITION
# ============================================================

balance_threshold = customer_profitability[
    "total_account_balance"
].quantile(0.75)

transaction_threshold = customer_profitability[
    "total_transaction_value"
].quantile(0.75)

customer_profitability[
    "high_value_customer_flag"
] = np.where(
    (
        customer_profitability[
            "total_account_balance"
        ] >= balance_threshold
    )
    |
    (
        customer_profitability[
            "total_transaction_value"
        ] >= transaction_threshold
    ),
    1,
    0
)

# ============================================================
# 21. COMBINED RISK LEVEL
# ============================================================

def combined_risk(row):

    fraud_risk = str(
        row.get(
            "customer_fraud_risk_level",
            ""
        )
    )

    loan_risk = str(
        row.get(
            "customer_loan_risk_level",
            ""
        )
    )

    if (
        fraud_risk == "Critical"
        or loan_risk == "Critical"
    ):
        return "Critical"

    elif (
        fraud_risk == "High"
        or loan_risk == "High"
    ):
        return "High"

    elif (
        fraud_risk == "Medium"
        or loan_risk == "Medium"
    ):
        return "Medium"

    else:
        return "Low"


customer_profitability[
    "combined_risk_level"
] = customer_profitability.apply(
    combined_risk,
    axis=1
)

print("\nCombined Risk Distribution:")

print(
    customer_profitability[
        "combined_risk_level"
    ].value_counts()
)

# ============================================================
# 22. HIGH-RISK + HIGH-VALUE CUSTOMERS
# ============================================================

print("\n" + "=" * 90)
print("11. HIGH-RISK + HIGH-VALUE CUSTOMERS")
print("=" * 90)

high_risk_high_value = customer_profitability[
    (
        customer_profitability[
            "high_value_customer_flag"
        ] == 1
    )
    &
    (
        customer_profitability[
            "combined_risk_level"
        ].isin(
            [
                "High",
                "Critical"
            ]
        )
    )
].copy()

high_risk_high_value = (
    high_risk_high_value
    .sort_values(
        "customer_profit",
        ascending=False
    )
)

print(
    "High-Risk + High-Value Customers:",
    len(high_risk_high_value)
)

print(
    high_risk_high_value[
        [
            "customer_id",
            "customer_name",
            "total_account_balance",
            "total_transaction_value",
            "customer_profit",
            "combined_risk_level"
        ]
    ].head(25)
)

# ============================================================
# 23. LOW-RISK + HIGH-VALUE CUSTOMERS
# ============================================================

print("\n" + "=" * 90)
print("12. LOW-RISK + HIGH-VALUE CUSTOMERS")
print("=" * 90)

low_risk_high_value = customer_profitability[
    (
        customer_profitability[
            "high_value_customer_flag"
        ] == 1
    )
    &
    (
        customer_profitability[
            "combined_risk_level"
        ] == "Low"
    )
].copy()

low_risk_high_value = (
    low_risk_high_value
    .sort_values(
        "customer_profit",
        ascending=False
    )
)

print(
    "Low-Risk + High-Value Customers:",
    len(low_risk_high_value)
)

print(
    low_risk_high_value[
        [
            "customer_id",
            "customer_name",
            "total_account_balance",
            "total_transaction_value",
            "customer_profit",
            "combined_risk_level"
        ]
    ].head(25)
)

# ============================================================
# 24. PROFITABILITY BY CUSTOMER SEGMENT
# ============================================================

print("\n" + "=" * 90)
print("13. PROFITABILITY BY CUSTOMER SEGMENT")
print("=" * 90)

segment_profitability = (
    customer_profitability
    .groupby(
        "customer_segment",
        dropna=False
    )
    .agg(
        total_customers=(
            "customer_id",
            "nunique"
        ),

        total_revenue=(
            "customer_revenue",
            "sum"
        ),

        total_operational_cost=(
            "customer_operational_cost",
            "sum"
        ),

        total_profit=(
            "customer_profit",
            "sum"
        ),

        average_profit=(
            "customer_profit",
            "mean"
        ),

        loss_making_customers=(
            "customer_profit",
            lambda x: (x < 0).sum()
        )
    )
    .reset_index()
)

segment_profitability[
    "profit_margin_pct"
] = np.where(
    segment_profitability[
        "total_revenue"
    ] > 0,

    segment_profitability[
        "total_profit"
    ]
    /
    segment_profitability[
        "total_revenue"
    ]
    * 100,

    0
)

print(
    segment_profitability
    .sort_values(
        "total_profit",
        ascending=False
    )
)

# ============================================================
# 25. CUSTOMER VALUE MATRIX
# ============================================================

print("\n" + "=" * 90)
print("14. CUSTOMER VALUE MATRIX")
print("=" * 90)

customer_profitability[
    "customer_value_category"
] = np.select(
    [
        (
            customer_profitability[
                "high_value_customer_flag"
            ] == 1
        )
        &
        (
            customer_profitability[
                "combined_risk_level"
            ].isin(
                ["High", "Critical"]
            )
        ),

        (
            customer_profitability[
                "high_value_customer_flag"
            ] == 1
        )
        &
        (
            customer_profitability[
                "combined_risk_level"
            ].isin(
                ["Low", "Medium"]
            )
        ),

        (
            customer_profitability[
                "high_value_customer_flag"
            ] == 0
        )
        &
        (
            customer_profitability[
                "combined_risk_level"
            ].isin(
                ["High", "Critical"]
            )
        )
    ],
    [
        "High Value - High Risk",
        "High Value - Low/Medium Risk",
        "Low Value - High Risk"
    ],
    default="Low Value - Low/Medium Risk"
)

print(
    customer_profitability[
        "customer_value_category"
    ].value_counts()
)

# ============================================================
# 26. BANK-LEVEL PROFITABILITY
# ============================================================

print("\n" + "=" * 90)
print("15. OVERALL CUSTOMER PROFITABILITY")
print("=" * 90)

total_revenue = customer_profitability[
    "customer_revenue"
].sum()

total_cost = customer_profitability[
    "customer_operational_cost"
].sum()

total_profit = customer_profitability[
    "customer_profit"
].sum()

overall_margin = (
    total_profit / total_revenue * 100
    if total_revenue != 0
    else 0
)

print(
    "Total Customer Revenue:",
    round(total_revenue, 2)
)

print(
    "Total Customer Operational Cost:",
    round(total_cost, 2)
)

print(
    "Total Customer Profit:",
    round(total_profit, 2)
)

print(
    "Overall Profit Margin:",
    round(overall_margin, 2),
    "%"
)

# ============================================================
# 27. SAVE OUTPUTS
# ============================================================

print("\n" + "=" * 90)
print("SAVING CUSTOMER PROFITABILITY RESULTS")
print("=" * 90)

customer_profitability.to_csv(
    os.path.join(
        output_path,
        "customer_profitability_analysis.csv"
    ),
    index=False
)

most_profitable_customers.to_csv(
    os.path.join(
        output_path,
        "most_profitable_customers.csv"
    ),
    index=False
)

loss_making_customers.to_csv(
    os.path.join(
        output_path,
        "loss_making_customers.csv"
    ),
    index=False
)

high_risk_high_value.to_csv(
    os.path.join(
        output_path,
        "high_risk_high_value_customers.csv"
    ),
    index=False
)

low_risk_high_value.to_csv(
    os.path.join(
        output_path,
        "low_risk_high_value_customers.csv"
    ),
    index=False
)

segment_profitability.to_csv(
    os.path.join(
        output_path,
        "profitability_by_customer_segment.csv"
    ),
    index=False
)

# ============================================================
# 28. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 90)
print("PART 5 - CUSTOMER PROFITABILITY SUMMARY")
print("=" * 90)

print(
    "\nTotal Customers:",
    len(customer_profitability)
)

print(
    "Total Revenue:",
    round(total_revenue, 2)
)

print(
    "Total Operational Cost:",
    round(total_cost, 2)
)

print(
    "Total Customer Profit:",
    round(total_profit, 2)
)

print(
    "Overall Profit Margin:",
    round(overall_margin, 2),
    "%"
)

print(
    "Profitable Customers:",
    (
        customer_profitability[
            "customer_profit"
        ] > 0
    ).sum()
)

print(
    "Loss-Making Customers:",
    (
        customer_profitability[
            "customer_profit"
        ] < 0
    ).sum()
)

print(
    "High-Risk + High-Value Customers:",
    len(high_risk_high_value)
)

print(
    "Low-Risk + High-Value Customers:",
    len(low_risk_high_value)
)

print("\nProfitability Segment Distribution:")

print(
    customer_profitability[
        "profitability_segment"
    ].value_counts()
)

print("\nCustomer Value Category Distribution:")

print(
    customer_profitability[
        "customer_value_category"
    ].value_counts()
)

print("\nFiles saved to:")
print(output_path)

print("\n" + "=" * 90)
print("PART 5 - CUSTOMER PROFITABILITY ANALYSIS COMPLETED SUCCESSFULLY")
print("=" * 90)