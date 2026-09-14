import pandas as pd
import numpy as np
import os

# ============================================================
# BANKING FRAUD, CUSTOMER RISK & PROFITABILITY ANALYTICS
# PART 4 - LOAN RISK ANALYSIS
# ============================================================

print("=" * 90)
print("PART 4 - LOAN RISK ANALYSIS")
print("=" * 90)

# ============================================================
# 1. PATHS
# ============================================================

cleaned_path = r"C:\Users\Hooooo\Documents\Excel\Banking Fraud Project\Cleaned Data"

output_path = r"C:\Users\Hooooo\Documents\Excel\Banking Fraud Project\Loan Risk Analysis"

os.makedirs(output_path, exist_ok=True)

print("\nCleaned Data Path:")
print(cleaned_path)

print("\nLoan Risk Output Path:")
print(output_path)

# ============================================================
# 2. LOAD DATASETS
# ============================================================

customers = pd.read_csv(
    os.path.join(cleaned_path, "customers_cleaned.csv")
)

loans = pd.read_csv(
    os.path.join(cleaned_path, "loans_cleaned.csv")
)

loan_payments = pd.read_csv(
    os.path.join(cleaned_path, "loan_payments_cleaned.csv")
)

credit_scores = pd.read_csv(
    os.path.join(cleaned_path, "credit_scores_cleaned.csv")
)

branches = pd.read_csv(
    os.path.join(cleaned_path, "branches_cleaned.csv")
)

print("\nDatasets loaded successfully!")

print("Customers:", customers.shape)
print("Loans:", loans.shape)
print("Loan Payments:", loan_payments.shape)
print("Credit Scores:", credit_scores.shape)
print("Branches:", branches.shape)

# ============================================================
# 3. BASIC CLEANING / STANDARDIZATION
# ============================================================

loans["default_status"] = (
    loans["default_status"]
    .astype(str)
    .str.strip()
    .str.title()
)

loans["loan_status"] = (
    loans["loan_status"]
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

loans["loan_start_date"] = pd.to_datetime(
    loans["loan_start_date"],
    errors="coerce"
)

loan_payments["due_date"] = pd.to_datetime(
    loan_payments["due_date"],
    errors="coerce"
)

loan_payments["payment_date"] = pd.to_datetime(
    loan_payments["payment_date"],
    errors="coerce"
)

credit_scores["score_date"] = pd.to_datetime(
    credit_scores["score_date"],
    errors="coerce"
)

# ============================================================
# 4. VALID LOAN RECORDS
# ============================================================

print("\n" + "=" * 90)
print("1. VALIDATE LOAN RECORDS")
print("=" * 90)

valid_customer_ids = set(customers["customer_id"].dropna())
valid_branch_ids = set(branches["branch_id"].dropna())

invalid_loan_customer = loans[
    ~loans["customer_id"].isin(valid_customer_ids)
].copy()

invalid_loan_branch = loans[
    ~loans["branch_id"].isin(valid_branch_ids)
].copy()

invalid_loan_values = loans[
    (loans["loan_amount"] <= 0)
    |
    (loans["interest_rate_pct"] < 0)
].copy()

print(
    "Loans With Invalid Customer:",
    len(invalid_loan_customer)
)

print(
    "Loans With Invalid Branch:",
    len(invalid_loan_branch)
)

print(
    "Loans With Invalid Financial Values:",
    len(invalid_loan_values)
)

# Keep only valid records for analysis
loans_analysis = loans[
    loans["customer_id"].isin(valid_customer_ids)
    &
    loans["branch_id"].isin(valid_branch_ids)
    &
    (loans["loan_amount"] > 0)
    &
    (loans["interest_rate_pct"] >= 0)
].copy()

print(
    "\nValid Loans For Analysis:",
    len(loans_analysis)
)

# ============================================================
# 5. CREDIT SCORE ANALYSIS
# ============================================================

print("\n" + "=" * 90)
print("2. CREDIT SCORE ANALYSIS")
print("=" * 90)

credit_scores_valid = credit_scores[
    credit_scores["customer_id"].isin(valid_customer_ids)
    &
    credit_scores["credit_score"].between(300, 900)
].copy()

credit_scores_valid["credit_score_band"] = pd.cut(
    credit_scores_valid["credit_score"],
    bins=[
        299,
        549,
        649,
        749,
        900
    ],
    labels=[
        "Poor",
        "Fair",
        "Good",
        "Excellent"
    ]
)

print("\nCredit Score Distribution:")

print(
    credit_scores_valid[
        "credit_score_band"
    ].value_counts().sort_index()
)

# ============================================================
# 6. REPAYMENT HISTORY
# ============================================================

print("\n" + "=" * 90)
print("3. REPAYMENT HISTORY")
print("=" * 90)

valid_loan_ids = set(
    loans_analysis["loan_id"].dropna()
)

payments_analysis = loan_payments[
    loan_payments["loan_id"].isin(valid_loan_ids)
    &
    (loan_payments["payment_amount"] > 0)
].copy()

payment_summary = (
    payments_analysis
    .groupby("loan_id")
    .agg(
        total_payment_records=(
            "payment_id",
            "count"
        ),

        total_amount_paid=(
            "payment_amount",
            "sum"
        ),

        paid_payments=(
            "payment_status",
            lambda x: (x == "Paid").sum()
        ),

        late_payments=(
            "days_late",
            lambda x: (x > 0).sum()
        ),

        max_days_late=(
            "days_late",
            "max"
        ),

        average_days_late=(
            "days_late",
            "mean"
        )
    )
    .reset_index()
)

payment_summary["repayment_rate_pct"] = (
    payment_summary["paid_payments"]
    /
    payment_summary["total_payment_records"]
    * 100
)

payment_summary["late_payment_rate_pct"] = (
    payment_summary["late_payments"]
    /
    payment_summary["total_payment_records"]
    * 100
)

print("\nRepayment Summary Sample:")

print(
    payment_summary.head(20)
)

# ============================================================
# 7. BUILD MASTER LOAN RISK TABLE
# ============================================================

loan_risk = pd.merge(
    loans_analysis,
    customers[
        [
            "customer_id",
            "customer_name",
            "customer_segment",
            "annual_income",
            "city",
            "home_branch_id",
            "declared_risk_segment"
        ]
    ],
    on="customer_id",
    how="left"
)

loan_risk = pd.merge(
    loan_risk,
    credit_scores_valid[
        [
            "customer_id",
            "credit_score",
            "credit_score_band",
            "past_due_accounts",
            "credit_utilization_pct",
            "hard_inquiries_12m",
            "credit_history_years"
        ]
    ],
    on="customer_id",
    how="left"
)

loan_risk = pd.merge(
    loan_risk,
    payment_summary,
    on="loan_id",
    how="left"
)

loan_risk = pd.merge(
    loan_risk,
    branches[
        [
            "branch_id",
            "branch_name",
            "city"
        ]
    ],
    on="branch_id",
    how="left",
    suffixes=("", "_branch")
)

# Fill missing payment summary values
payment_cols = [
    "total_payment_records",
    "total_amount_paid",
    "paid_payments",
    "late_payments",
    "max_days_late",
    "average_days_late",
    "repayment_rate_pct",
    "late_payment_rate_pct"
]

for col in payment_cols:
    loan_risk[col] = loan_risk[col].fillna(0)

# ============================================================
# 8. LOAN-TO-INCOME RATIO
# ============================================================

print("\n" + "=" * 90)
print("4. LOAN-TO-INCOME RATIO")
print("=" * 90)

loan_risk["loan_to_income_ratio"] = np.where(
    loan_risk["annual_income"] > 0,
    loan_risk["loan_amount"]
    /
    loan_risk["annual_income"],
    np.nan
)

print(
    loan_risk[
        [
            "customer_id",
            "customer_name",
            "annual_income",
            "loan_amount",
            "loan_to_income_ratio"
        ]
    ]
    .sort_values(
        "loan_to_income_ratio",
        ascending=False
    )
    .head(20)
)

# ============================================================
# 9. RISK FLAGS
# ============================================================

print("\n" + "=" * 90)
print("5. CREATE LOAN RISK FLAGS")
print("=" * 90)

loan_risk["low_credit_score_flag"] = np.where(
    loan_risk["credit_score"] < 600,
    1,
    0
)

loan_risk["high_utilization_flag"] = np.where(
    loan_risk["credit_utilization_pct"] >= 75,
    1,
    0
)

loan_risk["high_loan_to_income_flag"] = np.where(
    loan_risk["loan_to_income_ratio"] >= 1,
    1,
    0
)

loan_risk["high_interest_flag"] = np.where(
    loan_risk["interest_rate_pct"] >= 15,
    1,
    0
)

loan_risk["late_payment_flag"] = np.where(
    (
        loan_risk["max_days_late"] >= 30
    )
    |
    (
        loan_risk["days_past_due"] >= 30
    ),
    1,
    0
)

loan_risk["poor_repayment_flag"] = np.where(
    loan_risk["repayment_rate_pct"] < 80,
    1,
    0
)

loan_risk["past_due_accounts_flag"] = np.where(
    loan_risk["past_due_accounts"] >= 2,
    1,
    0
)

loan_risk["high_inquiry_flag"] = np.where(
    loan_risk["hard_inquiries_12m"] >= 5,
    1,
    0
)

loan_risk["default_flag"] = np.where(
    loan_risk["default_status"] == "Yes",
    1,
    0
)

# ============================================================
# 10. LOAN RISK SCORE
# ============================================================

print("\n" + "=" * 90)
print("6. CALCULATE LOAN RISK SCORE")
print("=" * 90)

loan_risk["loan_risk_score"] = (

    loan_risk["low_credit_score_flag"] * 20
    +
    loan_risk["high_utilization_flag"] * 10
    +
    loan_risk["high_loan_to_income_flag"] * 15
    +
    loan_risk["high_interest_flag"] * 10
    +
    loan_risk["late_payment_flag"] * 15
    +
    loan_risk["poor_repayment_flag"] * 10
    +
    loan_risk["past_due_accounts_flag"] * 10
    +
    loan_risk["high_inquiry_flag"] * 5
    +
    loan_risk["default_flag"] * 5
)

# Existing default should never appear as low-risk
loan_risk.loc[
    loan_risk["default_status"] == "Yes",
    "loan_risk_score"
] = (
    loan_risk.loc[
        loan_risk["default_status"] == "Yes",
        "loan_risk_score"
    ]
    .clip(lower=70)
)

loan_risk["loan_risk_level"] = pd.cut(
    loan_risk["loan_risk_score"],
    bins=[
        -1,
        24,
        49,
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

print("\nLoan Risk Distribution:")

print(
    loan_risk[
        "loan_risk_level"
    ].value_counts()
)

print("\nLoan Risk Score Statistics:")

print(
    loan_risk[
        "loan_risk_score"
    ].describe()
)

# ============================================================
# 11. OVERALL DEFAULT RATE
# ============================================================

print("\n" + "=" * 90)
print("7. OVERALL LOAN DEFAULT RATE")
print("=" * 90)

total_loans = len(loan_risk)

defaulted_loans = (
    loan_risk["default_status"] == "Yes"
).sum()

default_rate = (
    defaulted_loans
    / total_loans
    * 100
)

print("Total Loans:", total_loans)
print("Defaulted Loans:", defaulted_loans)
print(
    "Default Rate:",
    round(default_rate, 2),
    "%"
)

# ============================================================
# 12. DEFAULT BY CREDIT SCORE BAND
# ============================================================

print("\n" + "=" * 90)
print("8. DEFAULT BY CREDIT SCORE BAND")
print("=" * 90)

credit_default_analysis = (
    loan_risk
    .groupby(
        "credit_score_band",
        observed=False
    )
    .agg(
        total_loans=(
            "loan_id",
            "count"
        ),

        defaults=(
            "default_status",
            lambda x: (x == "Yes").sum()
        ),

        average_loan_amount=(
            "loan_amount",
            "mean"
        ),

        average_outstanding_balance=(
            "outstanding_balance",
            "mean"
        )
    )
    .reset_index()
)

credit_default_analysis[
    "default_rate_pct"
] = (
    credit_default_analysis["defaults"]
    /
    credit_default_analysis["total_loans"]
    * 100
)

print(
    credit_default_analysis
)

# ============================================================
# 13. HIGHEST-RISK CUSTOMER SEGMENTS
# ============================================================

print("\n" + "=" * 90)
print("9. HIGHEST-RISK CUSTOMER SEGMENTS")
print("=" * 90)

segment_risk = (
    loan_risk
    .groupby(
        "customer_segment",
        dropna=False
    )
    .agg(
        total_loans=(
            "loan_id",
            "count"
        ),

        total_loan_value=(
            "loan_amount",
            "sum"
        ),

        defaulted_loans=(
            "default_status",
            lambda x: (x == "Yes").sum()
        ),

        average_credit_score=(
            "credit_score",
            "mean"
        ),

        average_risk_score=(
            "loan_risk_score",
            "mean"
        ),

        high_critical_loans=(
            "loan_risk_level",
            lambda x: x.isin(
                ["High", "Critical"]
            ).sum()
        )
    )
    .reset_index()
)

segment_risk["default_rate_pct"] = (
    segment_risk["defaulted_loans"]
    /
    segment_risk["total_loans"]
    * 100
)

segment_risk["high_risk_pct"] = (
    segment_risk["high_critical_loans"]
    /
    segment_risk["total_loans"]
    * 100
)

print(
    segment_risk
    .sort_values(
        [
            "default_rate_pct",
            "average_risk_score"
        ],
        ascending=False
    )
)

# ============================================================
# 14. HIGHEST-RISK BRANCHES
# ============================================================

print("\n" + "=" * 90)
print("10. HIGHEST-RISK BRANCHES")
print("=" * 90)

branch_risk = (
    loan_risk
    .groupby(
        [
            "branch_id",
            "branch_name"
        ],
        dropna=False
    )
    .agg(
        total_loans=(
            "loan_id",
            "count"
        ),

        total_loan_value=(
            "loan_amount",
            "sum"
        ),

        outstanding_balance=(
            "outstanding_balance",
            "sum"
        ),

        defaulted_loans=(
            "default_status",
            lambda x: (x == "Yes").sum()
        ),

        average_credit_score=(
            "credit_score",
            "mean"
        ),

        average_risk_score=(
            "loan_risk_score",
            "mean"
        ),

        critical_loans=(
            "loan_risk_level",
            lambda x: (x == "Critical").sum()
        )
    )
    .reset_index()
)

branch_risk["default_rate_pct"] = (
    branch_risk["defaulted_loans"]
    /
    branch_risk["total_loans"]
    * 100
)

print(
    branch_risk
    .sort_values(
        [
            "default_rate_pct",
            "average_risk_score"
        ],
        ascending=False
    )
    .head(20)
)

# ============================================================
# 15. DEFAULT PATTERNS BY LOAN TYPE
# ============================================================

print("\n" + "=" * 90)
print("11. DEFAULT PATTERNS BY LOAN TYPE")
print("=" * 90)

loan_type_analysis = (
    loan_risk
    .groupby("loan_type")
    .agg(
        total_loans=(
            "loan_id",
            "count"
        ),

        total_loan_value=(
            "loan_amount",
            "sum"
        ),

        defaults=(
            "default_status",
            lambda x: (x == "Yes").sum()
        ),

        average_interest_rate=(
            "interest_rate_pct",
            "mean"
        ),

        average_days_past_due=(
            "days_past_due",
            "mean"
        ),

        average_risk_score=(
            "loan_risk_score",
            "mean"
        )
    )
    .reset_index()
)

loan_type_analysis["default_rate_pct"] = (
    loan_type_analysis["defaults"]
    /
    loan_type_analysis["total_loans"]
    * 100
)

print(
    loan_type_analysis
    .sort_values(
        "default_rate_pct",
        ascending=False
    )
)

# ============================================================
# 16. INCOME VS DEFAULT
# ============================================================

print("\n" + "=" * 90)
print("12. INCOME VS DEFAULT")
print("=" * 90)

loan_risk["income_band"] = pd.qcut(
    loan_risk["annual_income"],
    q=4,
    labels=[
        "Low Income",
        "Lower Middle",
        "Upper Middle",
        "High Income"
    ],
    duplicates="drop"
)

income_default_analysis = (
    loan_risk
    .groupby(
        "income_band",
        observed=False
    )
    .agg(
        total_loans=(
            "loan_id",
            "count"
        ),

        defaults=(
            "default_status",
            lambda x: (x == "Yes").sum()
        ),

        average_loan_amount=(
            "loan_amount",
            "mean"
        ),

        average_risk_score=(
            "loan_risk_score",
            "mean"
        )
    )
    .reset_index()
)

income_default_analysis["default_rate_pct"] = (
    income_default_analysis["defaults"]
    /
    income_default_analysis["total_loans"]
    * 100
)

print(income_default_analysis)

# ============================================================
# 17. INTEREST RATE VS DEFAULT
# ============================================================

print("\n" + "=" * 90)
print("13. INTEREST RATE VS DEFAULT")
print("=" * 90)

loan_risk["interest_rate_band"] = pd.cut(
    loan_risk["interest_rate_pct"],
    bins=[
        -0.01,
        8,
        12,
        16,
        np.inf
    ],
    labels=[
        "Low Rate",
        "Moderate Rate",
        "High Rate",
        "Very High Rate"
    ]
)

interest_default_analysis = (
    loan_risk
    .groupby(
        "interest_rate_band",
        observed=False
    )
    .agg(
        total_loans=(
            "loan_id",
            "count"
        ),

        defaults=(
            "default_status",
            lambda x: (x == "Yes").sum()
        ),

        average_loan_amount=(
            "loan_amount",
            "mean"
        )
    )
    .reset_index()
)

interest_default_analysis["default_rate_pct"] = (
    interest_default_analysis["defaults"]
    /
    interest_default_analysis["total_loans"]
    * 100
)

print(interest_default_analysis)

# ============================================================
# 18. LOAN AMOUNT VS DEFAULT
# ============================================================

print("\n" + "=" * 90)
print("14. LOAN AMOUNT VS DEFAULT")
print("=" * 90)

loan_risk["loan_amount_band"] = pd.qcut(
    loan_risk["loan_amount"],
    q=4,
    labels=[
        "Small Loan",
        "Medium Loan",
        "Large Loan",
        "Very Large Loan"
    ],
    duplicates="drop"
)

loan_amount_default_analysis = (
    loan_risk
    .groupby(
        "loan_amount_band",
        observed=False
    )
    .agg(
        total_loans=(
            "loan_id",
            "count"
        ),

        defaults=(
            "default_status",
            lambda x: (x == "Yes").sum()
        ),

        average_credit_score=(
            "credit_score",
            "mean"
        )
    )
    .reset_index()
)

loan_amount_default_analysis[
    "default_rate_pct"
] = (
    loan_amount_default_analysis["defaults"]
    /
    loan_amount_default_analysis["total_loans"]
    * 100
)

print(loan_amount_default_analysis)

# ============================================================
# 19. TOP HIGH-RISK LOANS
# ============================================================

print("\n" + "=" * 90)
print("15. TOP HIGH-RISK LOANS")
print("=" * 90)

top_high_risk_loans = (
    loan_risk
    .sort_values(
        [
            "loan_risk_score",
            "days_past_due",
            "outstanding_balance"
        ],
        ascending=False
    )
    .head(30)
    .copy()
)

print(
    top_high_risk_loans[
        [
            "loan_id",
            "customer_id",
            "customer_name",
            "loan_type",
            "loan_amount",
            "credit_score",
            "days_past_due",
            "repayment_rate_pct",
            "default_status",
            "loan_risk_score",
            "loan_risk_level"
        ]
    ]
)

# ============================================================
# 20. HIGH-RISK CUSTOMER SUMMARY
# ============================================================

customer_loan_risk = (
    loan_risk
    .groupby(
        [
            "customer_id",
            "customer_name",
            "customer_segment"
        ],
        dropna=False
    )
    .agg(
        total_loans=(
            "loan_id",
            "count"
        ),

        total_loan_value=(
            "loan_amount",
            "sum"
        ),

        total_outstanding_balance=(
            "outstanding_balance",
            "sum"
        ),

        average_credit_score=(
            "credit_score",
            "mean"
        ),

        max_days_past_due=(
            "days_past_due",
            "max"
        ),

        defaulted_loans=(
            "default_status",
            lambda x: (x == "Yes").sum()
        ),

        max_loan_risk_score=(
            "loan_risk_score",
            "max"
        ),

        average_loan_risk_score=(
            "loan_risk_score",
            "mean"
        )
    )
    .reset_index()
)

customer_loan_risk[
    "customer_loan_risk_level"
] = np.select(
    [
        (
            customer_loan_risk[
                "max_loan_risk_score"
            ] >= 70
        ),

        (
            customer_loan_risk[
                "max_loan_risk_score"
            ] >= 50
        ),

        (
            customer_loan_risk[
                "max_loan_risk_score"
            ] >= 25
        )
    ],
    [
        "Critical",
        "High",
        "Medium"
    ],
    default="Low"
)

print("\nCustomer Loan Risk Distribution:")

print(
    customer_loan_risk[
        "customer_loan_risk_level"
    ].value_counts()
)

# ============================================================
# 21. CREDIT SCORE VS DEFAULT SUMMARY
# ============================================================

print("\n" + "=" * 90)
print("16. CREDIT SCORE VS DEFAULT RELATIONSHIP")
print("=" * 90)

defaulted_credit_mean = loan_risk.loc[
    loan_risk["default_status"] == "Yes",
    "credit_score"
].mean()

non_default_credit_mean = loan_risk.loc[
    loan_risk["default_status"] != "Yes",
    "credit_score"
].mean()

print(
    "Average Credit Score - Defaulted Loans:",
    round(defaulted_credit_mean, 2)
)

print(
    "Average Credit Score - Non-Defaulted Loans:",
    round(non_default_credit_mean, 2)
)

difference = (
    non_default_credit_mean
    -
    defaulted_credit_mean
)

print(
    "Average Credit Score Difference:",
    round(difference, 2)
)

# ============================================================
# 22. SAVE OUTPUT FILES
# ============================================================

print("\n" + "=" * 90)
print("SAVING LOAN RISK ANALYSIS RESULTS")
print("=" * 90)

loan_risk.to_csv(
    os.path.join(
        output_path,
        "loan_risk_analysis.csv"
    ),
    index=False
)

customer_loan_risk.to_csv(
    os.path.join(
        output_path,
        "customer_loan_risk_summary.csv"
    ),
    index=False
)

segment_risk.to_csv(
    os.path.join(
        output_path,
        "loan_risk_by_customer_segment.csv"
    ),
    index=False
)

branch_risk.to_csv(
    os.path.join(
        output_path,
        "loan_risk_by_branch.csv"
    ),
    index=False
)

credit_default_analysis.to_csv(
    os.path.join(
        output_path,
        "default_by_credit_score_band.csv"
    ),
    index=False
)

loan_type_analysis.to_csv(
    os.path.join(
        output_path,
        "default_by_loan_type.csv"
    ),
    index=False
)

income_default_analysis.to_csv(
    os.path.join(
        output_path,
        "default_by_income_band.csv"
    ),
    index=False
)

interest_default_analysis.to_csv(
    os.path.join(
        output_path,
        "default_by_interest_rate.csv"
    ),
    index=False
)

loan_amount_default_analysis.to_csv(
    os.path.join(
        output_path,
        "default_by_loan_amount.csv"
    ),
    index=False
)

top_high_risk_loans.to_csv(
    os.path.join(
        output_path,
        "top_high_risk_loans.csv"
    ),
    index=False
)

invalid_loan_customer.to_csv(
    os.path.join(
        output_path,
        "invalid_loan_customer_records.csv"
    ),
    index=False
)

invalid_loan_branch.to_csv(
    os.path.join(
        output_path,
        "invalid_loan_branch_records.csv"
    ),
    index=False
)

invalid_loan_values.to_csv(
    os.path.join(
        output_path,
        "invalid_loan_value_records.csv"
    ),
    index=False
)

# ============================================================
# 23. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 90)
print("PART 4 - LOAN RISK ANALYSIS SUMMARY")
print("=" * 90)

print(
    "\nTotal Valid Loans:",
    len(loan_risk)
)

print(
    "Defaulted Loans:",
    defaulted_loans
)

print(
    "Overall Default Rate:",
    round(default_rate, 2),
    "%"
)

print(
    "Average Credit Score - Default:",
    round(defaulted_credit_mean, 2)
)

print(
    "Average Credit Score - Non Default:",
    round(non_default_credit_mean, 2)
)

print(
    "High / Critical Risk Loans:",
    loan_risk[
        "loan_risk_level"
    ].isin(
        [
            "High",
            "Critical"
        ]
    ).sum()
)

print(
    "High / Critical Risk Customers:",
    customer_loan_risk[
        "customer_loan_risk_level"
    ].isin(
        [
            "High",
            "Critical"
        ]
    ).sum()
)

print("\nLoan Risk Level Distribution:")

print(
    loan_risk[
        "loan_risk_level"
    ].value_counts()
)

print("\nFiles saved to:")
print(output_path)

print("\n" + "=" * 90)
print("PART 4 - LOAN RISK ANALYSIS COMPLETED SUCCESSFULLY")
print("=" * 90)