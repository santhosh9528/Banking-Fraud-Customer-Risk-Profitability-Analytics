import pandas as pd
import numpy as np
import os

# ============================================================
# BANKING FRAUD, CUSTOMER RISK & PROFITABILITY ANALYTICS
# PART 3 - FRAUD INVESTIGATION
# ============================================================

print("=" * 90)
print("PART 3 - FRAUD INVESTIGATION")
print("=" * 90)

# ============================================================
# 1. PATHS
# ============================================================

cleaned_path = r"C:\Users\Hooooo\Documents\Excel\Banking Fraud Project\Cleaned Data"

output_path = r"C:\Users\Hooooo\Documents\Excel\Banking Fraud Project\Fraud Analysis"

os.makedirs(output_path, exist_ok=True)

print("\nCleaned Data Path:")
print(cleaned_path)

print("\nFraud Analysis Output Path:")
print(output_path)

# ============================================================
# 2. LOAD DATASETS
# ============================================================

transactions = pd.read_csv(
    os.path.join(cleaned_path, "transactions_cleaned.csv")
)

customers = pd.read_csv(
    os.path.join(cleaned_path, "customers_cleaned.csv")
)

accounts = pd.read_csv(
    os.path.join(cleaned_path, "accounts_cleaned.csv")
)

login_activity = pd.read_csv(
    os.path.join(cleaned_path, "login_device_activity_cleaned.csv")
)

print("\nDatasets loaded successfully!")

print("\nTransactions:", transactions.shape)
print("Customers:", customers.shape)
print("Accounts:", accounts.shape)
print("Login Activity:", login_activity.shape)

# ============================================================
# 3. STANDARDIZE / PREPARE DATA
# ============================================================

transactions["transaction_datetime"] = pd.to_datetime(
    transactions["transaction_datetime"],
    errors="coerce"
)

login_activity["login_datetime"] = pd.to_datetime(
    login_activity["login_datetime"],
    errors="coerce"
)

accounts["open_date"] = pd.to_datetime(
    accounts["open_date"],
    errors="coerce"
)

accounts["last_activity_date"] = pd.to_datetime(
    accounts["last_activity_date"],
    errors="coerce"
)

transactions["transaction_status"] = (
    transactions["transaction_status"]
    .astype(str)
    .str.strip()
    .str.title()
)

transactions["fraud_confirmed"] = (
    transactions["fraud_confirmed"]
    .astype(str)
    .str.strip()
    .str.title()
)

login_activity["login_status"] = (
    login_activity["login_status"]
    .astype(str)
    .str.strip()
    .str.title()
)

transactions = transactions.dropna(
    subset=[
        "transaction_id",
        "customer_id",
        "transaction_datetime"
    ]
).copy()

transactions = transactions.sort_values(
    ["customer_id", "transaction_datetime"]
).reset_index(drop=True)

# ============================================================
# 4. MULTIPLE TRANSACTIONS WITHIN SHORT PERIOD
# ============================================================

print("\n" + "=" * 90)
print("1. RAPID REPEATED TRANSACTIONS")
print("=" * 90)

transactions["previous_transaction_time"] = (
    transactions
    .groupby("customer_id")["transaction_datetime"]
    .shift(1)
)

transactions["minutes_since_previous"] = (
    (
        transactions["transaction_datetime"]
        -
        transactions["previous_transaction_time"]
    )
    .dt.total_seconds()
    / 60
)

transactions["rapid_transaction_flag"] = np.where(
    (
        transactions["minutes_since_previous"] >= 0
    )
    &
    (
        transactions["minutes_since_previous"] <= 10
    ),
    1,
    0
)

rapid_transactions = transactions[
    transactions["rapid_transaction_flag"] == 1
].copy()

print(
    "Rapid Transactions Within 10 Minutes:",
    len(rapid_transactions)
)

print(
    rapid_transactions[
        [
            "transaction_id",
            "customer_id",
            "transaction_datetime",
            "transaction_amount",
            "minutes_since_previous"
        ]
    ].head(20)
)

# ============================================================
# 5. UNUSUAL TRANSACTION AMOUNT
# ============================================================

print("\n" + "=" * 90)
print("2. UNUSUAL TRANSACTION AMOUNTS")
print("=" * 90)

valid_amounts = transactions.loc[
    transactions["transaction_amount"] > 0,
    "transaction_amount"
]

Q1 = valid_amounts.quantile(0.25)
Q3 = valid_amounts.quantile(0.75)

IQR = Q3 - Q1

upper_bound = Q3 + (1.5 * IQR)

transactions["unusual_amount_flag"] = np.where(
    transactions["transaction_amount"] > upper_bound,
    1,
    0
)

unusual_amount_transactions = transactions[
    transactions["unusual_amount_flag"] == 1
].copy()

print("Q1:", round(Q1, 2))
print("Q3:", round(Q3, 2))
print("IQR:", round(IQR, 2))
print("Upper Bound:", round(upper_bound, 2))

print(
    "\nUnusual Transaction Amounts:",
    len(unusual_amount_transactions)
)

print(
    unusual_amount_transactions[
        [
            "transaction_id",
            "customer_id",
            "transaction_amount",
            "transaction_city",
            "channel"
        ]
    ]
    .sort_values(
        "transaction_amount",
        ascending=False
    )
    .head(20)
)

# ============================================================
# 6. SUDDEN LOCATION CHANGE
# ============================================================

print("\n" + "=" * 90)
print("3. SUDDEN LOCATION CHANGE")
print("=" * 90)

transactions["previous_city"] = (
    transactions
    .groupby("customer_id")["transaction_city"]
    .shift(1)
)

transactions["location_change_flag"] = np.where(
    transactions["previous_city"].notna()
    &
    (
        transactions["previous_city"]
        != transactions["transaction_city"]
    )
    &
    (
        transactions["minutes_since_previous"] >= 0
    )
    &
    (
        transactions["minutes_since_previous"] <= 180
    ),
    1,
    0
)

sudden_location_changes = transactions[
    transactions["location_change_flag"] == 1
].copy()

print(
    "Sudden Location Changes Within 3 Hours:",
    len(sudden_location_changes)
)

print(
    sudden_location_changes[
        [
            "transaction_id",
            "customer_id",
            "transaction_datetime",
            "previous_city",
            "transaction_city",
            "minutes_since_previous"
        ]
    ].head(20)
)

# ============================================================
# 7. MULTIPLE DEVICES
# ============================================================

print("\n" + "=" * 90)
print("4. MULTIPLE DEVICES")
print("=" * 90)

transaction_device_counts = (
    transactions
    .groupby("customer_id")["device_id"]
    .nunique()
    .reset_index(name="transaction_device_count")
)

login_device_counts = (
    login_activity
    .groupby("customer_id")["device_id"]
    .nunique()
    .reset_index(name="login_device_count")
)

device_summary = pd.merge(
    transaction_device_counts,
    login_device_counts,
    on="customer_id",
    how="outer"
)

device_summary[
    [
        "transaction_device_count",
        "login_device_count"
    ]
] = (
    device_summary[
        [
            "transaction_device_count",
            "login_device_count"
        ]
    ]
    .fillna(0)
)

device_summary["multiple_device_flag"] = np.where(
    (
        device_summary["transaction_device_count"] >= 4
    )
    |
    (
        device_summary["login_device_count"] >= 4
    ),
    1,
    0
)

multiple_device_customers = device_summary[
    device_summary["multiple_device_flag"] == 1
].copy()

print(
    "Customers Using Multiple / Unusual Devices:",
    len(multiple_device_customers)
)

print(
    multiple_device_customers
    .sort_values(
        [
            "transaction_device_count",
            "login_device_count"
        ],
        ascending=False
    )
    .head(20)
)

multiple_device_set = set(
    multiple_device_customers["customer_id"]
)

transactions["multiple_device_flag"] = np.where(
    transactions["customer_id"].isin(
        multiple_device_set
    ),
    1,
    0
)

# ============================================================
# 8. UNUSUAL MERCHANT ACTIVITY
# ============================================================

print("\n" + "=" * 90)
print("5. UNUSUAL MERCHANT ACTIVITY")
print("=" * 90)

merchant_customer_summary = (
    transactions
    .groupby(
        [
            "customer_id",
            "merchant_category"
        ]
    )
    .agg(
        merchant_transaction_count=(
            "transaction_id",
            "count"
        ),
        merchant_transaction_value=(
            "transaction_amount",
            "sum"
        )
    )
    .reset_index()
)

customer_total_transactions = (
    transactions
    .groupby("customer_id")
    .size()
    .reset_index(
        name="customer_total_transactions"
    )
)

merchant_customer_summary = pd.merge(
    merchant_customer_summary,
    customer_total_transactions,
    on="customer_id",
    how="left"
)

merchant_customer_summary[
    "merchant_frequency_pct"
] = (
    merchant_customer_summary[
        "merchant_transaction_count"
    ]
    /
    merchant_customer_summary[
        "customer_total_transactions"
    ]
    * 100
)

unusual_merchant_activity = (
    merchant_customer_summary[
        (
            merchant_customer_summary[
                "merchant_transaction_count"
            ] >= 5
        )
        &
        (
            merchant_customer_summary[
                "merchant_frequency_pct"
            ] >= 40
        )
    ]
    .copy()
)

print(
    "Unusual Merchant Activity Records:",
    len(unusual_merchant_activity)
)

print(
    unusual_merchant_activity
    .sort_values(
        "merchant_transaction_value",
        ascending=False
    )
    .head(20)
)

unusual_merchant_customers = set(
    unusual_merchant_activity["customer_id"]
)

transactions["unusual_merchant_flag"] = np.where(
    transactions["customer_id"].isin(
        unusual_merchant_customers
    ),
    1,
    0
)

# ============================================================
# 9. REPEATED FAILED TRANSACTIONS
# ============================================================

print("\n" + "=" * 90)
print("6. REPEATED FAILED TRANSACTIONS")
print("=" * 90)

failed_transactions = transactions[
    transactions["transaction_status"] == "Failed"
].copy()

failed_customer_summary = (
    failed_transactions
    .groupby("customer_id")
    .size()
    .reset_index(
        name="failed_transaction_count"
    )
)

repeated_failed_customers = (
    failed_customer_summary[
        failed_customer_summary[
            "failed_transaction_count"
        ] >= 3
    ]
    .copy()
)

print(
    "Customers With 3+ Failed Transactions:",
    len(repeated_failed_customers)
)

print(
    repeated_failed_customers
    .sort_values(
        "failed_transaction_count",
        ascending=False
    )
    .head(20)
)

repeated_failed_set = set(
    repeated_failed_customers["customer_id"]
)

transactions["repeated_failed_flag"] = np.where(
    transactions["customer_id"].isin(
        repeated_failed_set
    ),
    1,
    0
)

# ============================================================
# 10. FAILED LOGIN ACTIVITY
# ============================================================

print("\n" + "=" * 90)
print("7. FAILED LOGIN ACTIVITY")
print("=" * 90)

failed_login_activity = login_activity[
    (
        login_activity["login_status"] == "Failed"
    )
    |
    (
        login_activity["failed_attempt_count"] >= 3
    )
].copy()

failed_login_summary = (
    failed_login_activity
    .groupby("customer_id")
    .agg(
        suspicious_login_records=(
            "login_id",
            "count"
        ),
        max_failed_attempts=(
            "failed_attempt_count",
            "max"
        )
    )
    .reset_index()
)

high_failed_login_customers = (
    failed_login_summary[
        (
            failed_login_summary[
                "suspicious_login_records"
            ] >= 3
        )
        |
        (
            failed_login_summary[
                "max_failed_attempts"
            ] >= 3
        )
    ]
    .copy()
)

print(
    "Customers With Suspicious Login Activity:",
    len(high_failed_login_customers)
)

print(
    high_failed_login_customers
    .sort_values(
        "suspicious_login_records",
        ascending=False
    )
    .head(20)
)

failed_login_set = set(
    high_failed_login_customers["customer_id"]
)

transactions["failed_login_flag"] = np.where(
    transactions["customer_id"].isin(
        failed_login_set
    ),
    1,
    0
)

# ============================================================
# 11. HIGH-VALUE TRANSACTIONS AFTER DORMANT PERIOD
# ============================================================

print("\n" + "=" * 90)
print("8. HIGH-VALUE TRANSACTIONS AFTER DORMANT PERIOD")
print("=" * 90)

transactions["previous_customer_transaction"] = (
    transactions
    .groupby("customer_id")[
        "transaction_datetime"
    ]
    .shift(1)
)

transactions["days_since_previous"] = (
    (
        transactions["transaction_datetime"]
        -
        transactions[
            "previous_customer_transaction"
        ]
    )
    .dt.total_seconds()
    /
    86400
)

transactions[
    "high_value_after_dormant_flag"
] = np.where(
    (
        transactions["days_since_previous"] >= 30
    )
    &
    (
        transactions["transaction_amount"] >
        upper_bound
    ),
    1,
    0
)

high_value_after_dormant = transactions[
    transactions[
        "high_value_after_dormant_flag"
    ] == 1
].copy()

print(
    "High-Value Transactions After 30+ Days:",
    len(high_value_after_dormant)
)

print(
    high_value_after_dormant[
        [
            "transaction_id",
            "customer_id",
            "transaction_datetime",
            "days_since_previous",
            "transaction_amount"
        ]
    ].head(20)
)

# ============================================================
# 12. FRAUD RISK SCORE
# ============================================================

print("\n" + "=" * 90)
print("9. FRAUD RISK SCORE")
print("=" * 90)

# Weighted risk score out of 100

transactions["fraud_risk_score"] = (

    transactions["unusual_amount_flag"] * 20
    +
    transactions["rapid_transaction_flag"] * 15
    +
    transactions["location_change_flag"] * 20
    +
    transactions["multiple_device_flag"] * 10
    +
    transactions["unusual_merchant_flag"] * 10
    +
    transactions["repeated_failed_flag"] * 10
    +
    transactions["failed_login_flag"] * 5
    +
    transactions[
        "high_value_after_dormant_flag"
    ] * 10
)

# Optional boost for confirmed fraud
transactions.loc[
    transactions["fraud_confirmed"] == "Yes",
    "fraud_risk_score"
] = (
    transactions.loc[
        transactions["fraud_confirmed"] == "Yes",
        "fraud_risk_score"
    ]
    .clip(lower=70)
)

transactions["fraud_risk_level"] = pd.cut(
    transactions["fraud_risk_score"],
    bins=[
        -1,
        19,
        39,
        69,
        100
    ],
    labels=[
        "Low",
        "Medium",
        "High",
        "Critical"
    ]
)

print("\nFraud Risk Level Distribution:")

print(
    transactions[
        "fraud_risk_level"
    ].value_counts()
)

print("\nFraud Risk Score Statistics:")

print(
    transactions[
        "fraud_risk_score"
    ].describe()
)

# ============================================================
# 13. SUSPICIOUS TRANSACTIONS
# ============================================================

suspicious_transactions = transactions[
    transactions["fraud_risk_score"] >= 40
].copy()

print("\nSuspicious Transactions (Score >= 40):")
print(len(suspicious_transactions))

print(
    suspicious_transactions[
        [
            "transaction_id",
            "customer_id",
            "transaction_datetime",
            "transaction_amount",
            "fraud_risk_score",
            "fraud_risk_level",
            "fraud_confirmed"
        ]
    ]
    .sort_values(
        "fraud_risk_score",
        ascending=False
    )
    .head(30)
)

# ============================================================
# 14. CUSTOMER-LEVEL FRAUD RISK
# ============================================================

customer_fraud_summary = (
    transactions
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

        suspicious_transactions=(
            "fraud_risk_score",
            lambda x: (x >= 40).sum()
        ),

        max_fraud_risk_score=(
            "fraud_risk_score",
            "max"
        ),

        average_fraud_risk_score=(
            "fraud_risk_score",
            "mean"
        ),

        confirmed_fraud_transactions=(
            "fraud_confirmed",
            lambda x: (
                x.astype(str).str.title()
                == "Yes"
            ).sum()
        )
    )
    .reset_index()
)

customer_fraud_summary = pd.merge(
    customer_fraud_summary,
    customers[
        [
            "customer_id",
            "customer_name",
            "customer_segment",
            "city",
            "annual_income",
            "declared_risk_segment"
        ]
    ],
    on="customer_id",
    how="left"
)

customer_fraud_summary[
    "customer_fraud_risk_level"
] = np.select(
    [
        (
            customer_fraud_summary[
                "max_fraud_risk_score"
            ] >= 70
        )
        |
        (
            customer_fraud_summary[
                "confirmed_fraud_transactions"
            ] > 0
        ),

        customer_fraud_summary[
            "max_fraud_risk_score"
        ] >= 40,

        customer_fraud_summary[
            "max_fraud_risk_score"
        ] >= 20
    ],
    [
        "Critical",
        "High",
        "Medium"
    ],
    default="Low"
)

print("\nCustomer Fraud Risk Distribution:")

print(
    customer_fraud_summary[
        "customer_fraud_risk_level"
    ].value_counts()
)

print("\nTop High-Risk Customers:")

print(
    customer_fraud_summary[
        [
            "customer_id",
            "customer_name",
            "customer_segment",
            "total_transactions",
            "suspicious_transactions",
            "max_fraud_risk_score",
            "confirmed_fraud_transactions",
            "customer_fraud_risk_level"
        ]
    ]
    .sort_values(
        [
            "max_fraud_risk_score",
            "suspicious_transactions"
        ],
        ascending=False
    )
    .head(20)
)

# ============================================================
# 15. FRAUD BY CUSTOMER SEGMENT
# ============================================================

fraud_segment_analysis = (
    customer_fraud_summary
    .groupby(
        "customer_segment",
        dropna=False
    )
    .agg(
        total_customers=(
            "customer_id",
            "nunique"
        ),

        suspicious_customers=(
            "customer_fraud_risk_level",
            lambda x: x.isin(
                ["High", "Critical"]
            ).sum()
        ),

        total_suspicious_transactions=(
            "suspicious_transactions",
            "sum"
        )
    )
    .reset_index()
)

fraud_segment_analysis[
    "high_risk_customer_pct"
] = (
    fraud_segment_analysis[
        "suspicious_customers"
    ]
    /
    fraud_segment_analysis[
        "total_customers"
    ]
    * 100
)

print("\nFraud by Customer Segment:")

print(
    fraud_segment_analysis
    .sort_values(
        "high_risk_customer_pct",
        ascending=False
    )
)

# ============================================================
# 16. FRAUD BY BRANCH
# ============================================================

fraud_branch_analysis = (
    transactions
    .groupby("branch_id")
    .agg(
        total_transactions=(
            "transaction_id",
            "count"
        ),

        total_transaction_value=(
            "transaction_amount",
            "sum"
        ),

        suspicious_transactions=(
            "fraud_risk_score",
            lambda x: (x >= 40).sum()
        ),

        suspicious_amount=(
            "transaction_amount",
            lambda x: x[
                transactions.loc[
                    x.index,
                    "fraud_risk_score"
                ] >= 40
            ].sum()
        ),

        confirmed_fraud_transactions=(
            "fraud_confirmed",
            lambda x: (
                x.astype(str).str.title()
                == "Yes"
            ).sum()
        )
    )
    .reset_index()
)

fraud_branch_analysis[
    "suspicious_transaction_pct"
] = (
    fraud_branch_analysis[
        "suspicious_transactions"
    ]
    /
    fraud_branch_analysis[
        "total_transactions"
    ]
    * 100
)

print("\nFraud by Branch:")

print(
    fraud_branch_analysis
    .sort_values(
        "suspicious_transactions",
        ascending=False
    )
    .head(20)
)

# ============================================================
# 17. FRAUD DETECTION PERFORMANCE
# ============================================================

print("\n" + "=" * 90)
print("10. FRAUD FLAG VS CONFIRMED FRAUD")
print("=" * 90)

transactions["predicted_fraud"] = np.where(
    transactions["fraud_risk_score"] >= 40,
    "Yes",
    "No"
)

fraud_validation = pd.crosstab(
    transactions["fraud_confirmed"],
    transactions["predicted_fraud"],
    margins=True
)

print("\nFraud Confirmation vs Predicted Fraud:")
print(fraud_validation)

# ============================================================
# 18. TOP 20 HIGHEST-RISK TRANSACTIONS
# ============================================================

top_risk_transactions = (
    transactions
    .sort_values(
        [
            "fraud_risk_score",
            "transaction_amount"
        ],
        ascending=False
    )
    .head(20)
    .copy()
)

print("\nTop 20 Highest-Risk Transactions:")

print(
    top_risk_transactions[
        [
            "transaction_id",
            "customer_id",
            "transaction_datetime",
            "transaction_amount",
            "transaction_city",
            "fraud_risk_score",
            "fraud_risk_level",
            "fraud_confirmed"
        ]
    ]
)

# ============================================================
# 19. SAVE FRAUD ANALYSIS RESULTS
# ============================================================

print("\n" + "=" * 90)
print("SAVING FRAUD ANALYSIS RESULTS")
print("=" * 90)

# Remove temporary helper columns only from final transaction file
fraud_transactions_output = transactions.copy()

helper_columns = [
    "previous_transaction_time",
    "minutes_since_previous",
    "previous_city",
    "previous_customer_transaction",
    "days_since_previous"
]

fraud_transactions_output.drop(
    columns=helper_columns,
    errors="ignore",
    inplace=True
)

fraud_transactions_output.to_csv(
    os.path.join(
        output_path,
        "transactions_with_fraud_risk.csv"
    ),
    index=False
)

suspicious_transactions.to_csv(
    os.path.join(
        output_path,
        "suspicious_transactions.csv"
    ),
    index=False
)

customer_fraud_summary.to_csv(
    os.path.join(
        output_path,
        "customer_fraud_risk_summary.csv"
    ),
    index=False
)

rapid_transactions.to_csv(
    os.path.join(
        output_path,
        "rapid_repeated_transactions.csv"
    ),
    index=False
)

unusual_amount_transactions.to_csv(
    os.path.join(
        output_path,
        "unusual_transaction_amounts.csv"
    ),
    index=False
)

sudden_location_changes.to_csv(
    os.path.join(
        output_path,
        "sudden_location_changes.csv"
    ),
    index=False
)

multiple_device_customers.to_csv(
    os.path.join(
        output_path,
        "multiple_device_customers.csv"
    ),
    index=False
)

unusual_merchant_activity.to_csv(
    os.path.join(
        output_path,
        "unusual_merchant_activity.csv"
    ),
    index=False
)

repeated_failed_customers.to_csv(
    os.path.join(
        output_path,
        "repeated_failed_transaction_customers.csv"
    ),
    index=False
)

high_failed_login_customers.to_csv(
    os.path.join(
        output_path,
        "suspicious_login_customers.csv"
    ),
    index=False
)

high_value_after_dormant.to_csv(
    os.path.join(
        output_path,
        "high_value_after_dormant_period.csv"
    ),
    index=False
)

fraud_segment_analysis.to_csv(
    os.path.join(
        output_path,
        "fraud_by_customer_segment.csv"
    ),
    index=False
)

fraud_branch_analysis.to_csv(
    os.path.join(
        output_path,
        "fraud_by_branch.csv"
    ),
    index=False
)

top_risk_transactions.to_csv(
    os.path.join(
        output_path,
        "top_20_highest_risk_transactions.csv"
    ),
    index=False
)

# ============================================================
# 20. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 90)
print("PART 3 - FRAUD INVESTIGATION SUMMARY")
print("=" * 90)

print(
    "\nTotal Transactions:",
    len(transactions)
)

print(
    "Rapid Transactions:",
    len(rapid_transactions)
)

print(
    "Unusual Amount Transactions:",
    len(unusual_amount_transactions)
)

print(
    "Sudden Location Changes:",
    len(sudden_location_changes)
)

print(
    "Multiple Device Customers:",
    len(multiple_device_customers)
)

print(
    "Unusual Merchant Activity Records:",
    len(unusual_merchant_activity)
)

print(
    "Repeated Failed Transaction Customers:",
    len(repeated_failed_customers)
)

print(
    "Suspicious Login Customers:",
    len(high_failed_login_customers)
)

print(
    "High-Value Transactions After Dormant Period:",
    len(high_value_after_dormant)
)

print(
    "Suspicious Transactions Score >= 40:",
    len(suspicious_transactions)
)

print(
    "High / Critical Risk Customers:",
    customer_fraud_summary[
        "customer_fraud_risk_level"
    ]
    .isin(
        [
            "High",
            "Critical"
        ]
    )
    .sum()
)

print("\nFraud Risk Level Distribution:")

print(
    transactions[
        "fraud_risk_level"
    ]
    .value_counts()
)

print("\nFiles saved to:")
print(output_path)

print("\n" + "=" * 90)
print("PART 3 - FRAUD INVESTIGATION COMPLETED SUCCESSFULLY")
print("=" * 90)