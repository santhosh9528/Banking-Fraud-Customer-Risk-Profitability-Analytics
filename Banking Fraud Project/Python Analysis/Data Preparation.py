import pandas as pd
import numpy as np
import os

# ============================================================
# BANKING FRAUD, CUSTOMER RISK & PROFITABILITY ANALYTICS
# PART 1 - DATA PREPARATION
# ============================================================

print("=" * 80)
print("PART 1 - DATA PREPARATION")
print("=" * 80)

# ============================================================
# 1. FILE PATHS
# ============================================================

# Raw CSV files path
base_path = r"C:\Users\Hooooo\Documents\Excel\Banking Fraud Project\Rawdata"

# Cleaned datasets output path
cleaned_output_path = r"C:\Users\Hooooo\Documents\Excel\Banking Fraud Project\Cleaned Data"

# Data quality reports output path
report_output_path = r"C:\Users\Hooooo\Documents\Excel\Banking Fraud Project\Data Quality report"

os.makedirs(cleaned_output_path, exist_ok=True)
os.makedirs(report_output_path, exist_ok=True)

print("\nRaw Data Path:")
print(base_path)

print("\nCleaned Data Path:")
print(cleaned_output_path)

print("\nData Quality Report Path:")
print(report_output_path)

# ============================================================
# 2. LOAD DATASETS
# ============================================================

customers = pd.read_csv(
    os.path.join(base_path, "customers.csv")
)

accounts = pd.read_csv(
    os.path.join(base_path, "accounts.csv")
)

transactions = pd.read_csv(
    os.path.join(base_path, "transactions.csv")
)

loans = pd.read_csv(
    os.path.join(base_path, "loans.csv")
)

loan_payments = pd.read_csv(
    os.path.join(base_path, "loan_payments.csv")
)

credit_scores = pd.read_csv(
    os.path.join(base_path, "credit_scores.csv")
)

branches = pd.read_csv(
    os.path.join(base_path, "branches.csv")
)

complaints = pd.read_csv(
    os.path.join(base_path, "complaints.csv")
)

login_activity = pd.read_csv(
    os.path.join(base_path, "login_device_activity.csv")
)

print("\nAll datasets loaded successfully!")

# ============================================================
# 3. DATASET OVERVIEW
# ============================================================

datasets = {
    "Customers": customers,
    "Accounts": accounts,
    "Transactions": transactions,
    "Loans": loans,
    "Loan Payments": loan_payments,
    "Credit Scores": credit_scores,
    "Branches": branches,
    "Complaints": complaints,
    "Login Device Activity": login_activity
}

print("\n" + "=" * 80)
print("DATASET OVERVIEW")
print("=" * 80)

for name, df in datasets.items():

    print(
        f"{name:<25} "
        f"Rows: {df.shape[0]:>7} | "
        f"Columns: {df.shape[1]}"
    )

# ============================================================
# PART 1.1 - IDENTIFY DUPLICATE CUSTOMERS
# ============================================================

print("\n" + "=" * 80)
print("1. IDENTIFY DUPLICATE CUSTOMERS")
print("=" * 80)

exact_duplicates = customers[
    customers.duplicated(keep=False)
].copy()

print("\nExact Duplicate Customer Rows:")
print(exact_duplicates)

print(
    "\nTotal rows involved in exact duplicates:",
    len(exact_duplicates)
)

duplicate_customer_ids = customers[
    customers.duplicated(
        subset=["customer_id"],
        keep=False
    )
].copy()

print("\nDuplicate Customer IDs:")

print(
    duplicate_customer_ids[
        [
            "customer_id",
            "customer_name",
            "email",
            "phone"
        ]
    ]
)

duplicate_emails = customers[
    customers.duplicated(
        subset=["email"],
        keep=False
    )
].copy()

duplicate_phones = customers[
    customers.duplicated(
        subset=["phone"],
        keep=False
    )
].copy()

# Remove exact duplicates
customers = customers.drop_duplicates().copy()

print(
    "\nCustomers after removing exact duplicates:",
    len(customers)
)

# ============================================================
# PART 1.2 - HANDLE MISSING VALUES
# ============================================================

print("\n" + "=" * 80)
print("2. HANDLE MISSING VALUES")
print("=" * 80)

print("\nMissing Values Before Cleaning:\n")

for name, df in datasets.items():

    missing = df.isnull().sum()
    missing = missing[missing > 0]

    if len(missing) > 0:

        print(f"\n{name}:")
        print(missing)

# Remove customers without customer_id
customers = customers.dropna(
    subset=["customer_id"]
).copy()

# Fill missing annual income with median
customers["annual_income"] = (
    customers["annual_income"]
    .fillna(customers["annual_income"].median())
)

# Fill payment status if missing
loan_payments["payment_status"] = (
    loan_payments["payment_status"]
    .fillna("Unknown")
)

# ============================================================
# PART 1.3 - DETECT INVALID TRANSACTIONS
# ============================================================

print("\n" + "=" * 80)
print("3. DETECT INVALID TRANSACTIONS")
print("=" * 80)

invalid_amount = transactions[
    transactions["transaction_amount"] <= 0
].copy()

print(
    "\nInvalid Transaction Amounts:",
    len(invalid_amount)
)

valid_account_ids = set(
    accounts["account_id"].dropna()
)

invalid_transaction_accounts = transactions[
    ~transactions["account_id"].isin(valid_account_ids)
].copy()

print(
    "Transactions With Invalid Account IDs:",
    len(invalid_transaction_accounts)
)

missing_transaction_customer = transactions[
    transactions["customer_id"].isna()
].copy()

print(
    "Transactions With Missing Customer ID:",
    len(missing_transaction_customer)
)

transactions["transaction_status"] = (
    transactions["transaction_status"]
    .astype("string")
    .str.strip()
    .str.title()
)

valid_status = [
    "Success",
    "Failed",
    "Reversed"
]

invalid_status = transactions[
    ~transactions["transaction_status"].isin(valid_status)
].copy()

print(
    "Invalid Transaction Status:",
    len(invalid_status)
)

# ============================================================
# PART 1.4 - STANDARDIZE DATES AND CURRENCIES
# ============================================================

print("\n" + "=" * 80)
print("4. STANDARDIZE DATES AND CURRENCIES")
print("=" * 80)

for df in [accounts, transactions]:

    df["currency"] = (
        df["currency"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

customers["join_date"] = pd.to_datetime(
    customers["join_date"],
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

transactions["transaction_datetime"] = pd.to_datetime(
    transactions["transaction_datetime"],
    errors="coerce"
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

branches["open_date"] = pd.to_datetime(
    branches["open_date"],
    errors="coerce"
)

complaints["complaint_date"] = pd.to_datetime(
    complaints["complaint_date"],
    errors="coerce"
)

complaints["resolved_date"] = pd.to_datetime(
    complaints["resolved_date"],
    errors="coerce"
)

login_activity["login_datetime"] = pd.to_datetime(
    login_activity["login_datetime"],
    errors="coerce"
)

invalid_transaction_dates = transactions[
    transactions["transaction_datetime"].isna()
].copy()

invalid_login_dates = login_activity[
    login_activity["login_datetime"].isna()
].copy()

print(
    "\nInvalid Transaction Dates:",
    len(invalid_transaction_dates)
)

print(
    "Invalid Login Dates:",
    len(invalid_login_dates)
)

transactions = transactions[
    transactions["transaction_datetime"].notna()
].copy()

login_activity = login_activity[
    login_activity["login_datetime"].notna()
].copy()

# ============================================================
# PART 1.5 - VALIDATE ACCOUNT RELATIONSHIPS
# ============================================================

print("\n" + "=" * 80)
print("5. VALIDATE ACCOUNT RELATIONSHIPS")
print("=" * 80)

valid_customer_ids = set(
    customers["customer_id"].dropna()
)

valid_branch_ids = set(
    branches["branch_id"].dropna()
)

invalid_account_customer = accounts[
    ~accounts["customer_id"].isin(valid_customer_ids)
].copy()

print(
    "\nAccounts With Invalid Customer ID:",
    len(invalid_account_customer)
)

invalid_account_branch = accounts[
    ~accounts["branch_id"].isin(valid_branch_ids)
].copy()

print(
    "Accounts With Invalid Branch ID:",
    len(invalid_account_branch)
)

account_customer_map = (
    accounts
    .drop_duplicates(subset=["account_id"])
    .set_index("account_id")["customer_id"]
)

transactions["expected_customer_id"] = (
    transactions["account_id"]
    .map(account_customer_map)
)

account_customer_mismatch = transactions[
    transactions["expected_customer_id"].notna()
    &
    (
        transactions["customer_id"]
        != transactions["expected_customer_id"]
    )
].copy()

print(
    "Transaction Account-Customer Mismatches:",
    len(account_customer_mismatch)
)

transactions.drop(
    columns=["expected_customer_id"],
    inplace=True
)

# ============================================================
# PART 1.6 - DETECT INCONSISTENT CUSTOMER INFORMATION
# ============================================================

print("\n" + "=" * 80)
print("6. DETECT INCONSISTENT CUSTOMER INFORMATION")
print("=" * 80)

text_columns = [
    "customer_name",
    "gender",
    "city",
    "state",
    "customer_segment",
    "occupation",
    "declared_risk_segment"
]

for column in text_columns:

    customers[column] = (
        customers[column]
        .astype("string")
        .str.strip()
    )

customers["city"] = customers["city"].str.title()
customers["state"] = customers["state"].str.title()
customers["customer_segment"] = customers["customer_segment"].str.title()
customers["occupation"] = customers["occupation"].str.title()
customers["gender"] = customers["gender"].str.title()
customers["declared_risk_segment"] = customers["declared_risk_segment"].str.title()

customers["email"] = (
    customers["email"]
    .astype("string")
    .str.strip()
    .str.lower()
)

invalid_age = customers[
    (customers["age"] < 18)
    |
    (customers["age"] > 100)
].copy()

invalid_income = customers[
    customers["annual_income"] <= 0
].copy()

invalid_customer_branch = customers[
    ~customers["home_branch_id"].isin(valid_branch_ids)
].copy()

print(
    "\nInvalid Customer Ages:",
    len(invalid_age)
)

print(
    "Invalid Customer Income:",
    len(invalid_income)
)

print(
    "Customers With Invalid Home Branch:",
    len(invalid_customer_branch)
)

# ============================================================
# PART 1.7 - IDENTIFY UNUSUAL TRANSACTION PATTERNS
# ============================================================

print("\n" + "=" * 80)
print("7. IDENTIFY UNUSUAL TRANSACTION PATTERNS")
print("=" * 80)

valid_positive_amounts = transactions.loc[
    transactions["transaction_amount"] > 0,
    "transaction_amount"
]

Q1 = valid_positive_amounts.quantile(0.25)
Q3 = valid_positive_amounts.quantile(0.75)

IQR = Q3 - Q1

upper_bound = Q3 + (1.5 * IQR)

high_value_transactions = transactions[
    transactions["transaction_amount"] > upper_bound
].copy()

print(
    "\nHigh-Value Transactions:",
    len(high_value_transactions)
)

# Sort for time-based analysis
transactions = transactions.sort_values(
    [
        "customer_id",
        "transaction_datetime"
    ]
).copy()

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

rapid_transactions = transactions[
    (transactions["minutes_since_previous"] >= 0)
    &
    (transactions["minutes_since_previous"] <= 10)
].copy()

print(
    "Rapid Transactions:",
    len(rapid_transactions)
)

device_counts = (
    transactions
    .groupby("customer_id")["device_id"]
    .nunique()
    .reset_index(name="unique_devices")
)

multiple_device_customers = device_counts[
    device_counts["unique_devices"] > 1
].copy()

login_device_counts = (
    login_activity
    .groupby("customer_id")["device_id"]
    .nunique()
    .reset_index(name="login_device_count")
)

unusual_login_devices = login_device_counts[
    login_device_counts["login_device_count"] > 2
].copy()

failed_transactions = transactions[
    transactions["transaction_status"] == "Failed"
].copy()

failed_transaction_counts = (
    failed_transactions
    .groupby("customer_id")
    .size()
    .reset_index(
        name="failed_transaction_count"
    )
)

repeated_failed_transactions = (
    failed_transaction_counts[
        failed_transaction_counts[
            "failed_transaction_count"
        ] >= 3
    ]
).copy()

login_activity["login_status"] = (
    login_activity["login_status"]
    .astype("string")
    .str.strip()
    .str.title()
)

failed_logins = login_activity[
    login_activity["login_status"] == "Failed"
].copy()

high_failed_logins = failed_logins[
    failed_logins["failed_attempt_count"] >= 3
].copy()

transactions["previous_city"] = (
    transactions
    .groupby("customer_id")[
        "transaction_city"
    ]
    .shift(1)
)

location_changes = transactions[
    transactions["previous_city"].notna()
    &
    (
        transactions["transaction_city"]
        != transactions["previous_city"]
    )
    &
    (
        transactions["minutes_since_previous"] >= 0
    )
    &
    (
        transactions["minutes_since_previous"] <= 180
    )
].copy()

print(
    "Sudden Location Changes:",
    len(location_changes)
)

# ============================================================
# TRANSACTION CLEANING
# ============================================================

print("\n" + "=" * 80)
print("TRANSACTION CLEANING")
print("=" * 80)

before_transactions = len(transactions)

transactions = transactions[
    transactions["transaction_amount"] > 0
].copy()

valid_account_ids = set(
    accounts["account_id"].dropna()
)

transactions = transactions[
    transactions["account_id"].isin(valid_account_ids)
].copy()

account_customer_lookup = (
    accounts
    .drop_duplicates(subset=["account_id"])
    .set_index("account_id")["customer_id"]
)

missing_customer_mask = (
    transactions["customer_id"].isna()
)

transactions.loc[
    missing_customer_mask,
    "customer_id"
] = (
    transactions.loc[
        missing_customer_mask,
        "account_id"
    ]
    .map(account_customer_lookup)
)

transactions = transactions.dropna(
    subset=["customer_id"]
).copy()

after_transactions = len(transactions)

print(
    "Transactions Before Cleaning:",
    before_transactions
)

print(
    "Transactions After Cleaning:",
    after_transactions
)

print(
    "Transactions Removed:",
    before_transactions - after_transactions
)

# ============================================================
# CREATE BASIC FRAUD FLAGS
# ============================================================

transactions["high_value_flag"] = np.where(
    transactions["transaction_amount"] > upper_bound,
    1,
    0
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

transactions["location_change_flag"] = np.where(
    transactions["previous_city"].notna()
    &
    (
        transactions["transaction_city"]
        != transactions["previous_city"]
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

transactions["failed_transaction_flag"] = np.where(
    transactions["transaction_status"] == "Failed",
    1,
    0
)

transactions["basic_fraud_flag_count"] = (
    transactions["high_value_flag"]
    + transactions["rapid_transaction_flag"]
    + transactions["location_change_flag"]
    + transactions["failed_transaction_flag"]
)

# ============================================================
# REMOVE DUPLICATES
# ============================================================

accounts = accounts.drop_duplicates().copy()
loans = loans.drop_duplicates().copy()
loan_payments = loan_payments.drop_duplicates().copy()
credit_scores = credit_scores.drop_duplicates().copy()
branches = branches.drop_duplicates().copy()
complaints = complaints.drop_duplicates().copy()
login_activity = login_activity.drop_duplicates().copy()

# ============================================================
# SAVE DATA QUALITY REPORTS
# ============================================================

print("\n" + "=" * 80)
print("SAVE DATA QUALITY REPORTS")
print("=" * 80)

quality_reports = {
    "duplicate_customers_report.csv": exact_duplicates,
    "invalid_transactions_report.csv": invalid_amount,
    "invalid_transaction_account_relationships.csv": invalid_transaction_accounts,
    "invalid_transaction_dates.csv": invalid_transaction_dates,
    "invalid_login_dates.csv": invalid_login_dates,
    "invalid_account_customer_relationships.csv": invalid_account_customer,
    "invalid_account_branch_relationships.csv": invalid_account_branch,
    "transaction_customer_mismatch_report.csv": account_customer_mismatch,
    "high_value_transactions.csv": high_value_transactions,
    "rapid_transactions.csv": rapid_transactions,
    "sudden_location_changes.csv": location_changes,
    "repeated_failed_transaction_customers.csv": repeated_failed_transactions,
    "multiple_transaction_device_customers.csv": multiple_device_customers,
    "multiple_login_device_customers.csv": unusual_login_devices,
    "high_failed_login_attempts.csv": high_failed_logins
}

for filename, dataframe in quality_reports.items():

    dataframe.to_csv(
        os.path.join(
            report_output_path,
            filename
        ),
        index=False
    )

print(
    "\nTotal Data Quality Report Files Saved:",
    len(quality_reports)
)

print("\nReports Saved To:")
print(report_output_path)

# ============================================================
# REMOVE TEMPORARY HELPER COLUMNS
# ============================================================

temporary_columns = [
    "previous_transaction_time",
    "minutes_since_previous",
    "previous_city"
]

transactions.drop(
    columns=temporary_columns,
    errors="ignore",
    inplace=True
)

# ============================================================
# SAVE CLEANED DATASETS
# ============================================================

print("\n" + "=" * 80)
print("SAVE CLEANED DATASETS")
print("=" * 80)

cleaned_files = {
    "customers_cleaned.csv": customers,
    "accounts_cleaned.csv": accounts,
    "transactions_cleaned.csv": transactions,
    "loans_cleaned.csv": loans,
    "loan_payments_cleaned.csv": loan_payments,
    "credit_scores_cleaned.csv": credit_scores,
    "branches_cleaned.csv": branches,
    "complaints_cleaned.csv": complaints,
    "login_device_activity_cleaned.csv": login_activity
}

for filename, dataframe in cleaned_files.items():

    dataframe.to_csv(
        os.path.join(
            cleaned_output_path,
            filename
        ),
        index=False
    )

print(
    "\nTotal Cleaned Dataset Files Saved:",
    len(cleaned_files)
)

print("\nCleaned Files Saved To:")
print(cleaned_output_path)

# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("PART 1 - DATA PREPARATION SUMMARY")
print("=" * 80)

print(
    "\nDuplicate customer rows identified:",
    len(exact_duplicates)
)

print(
    "Invalid transaction amounts:",
    len(invalid_amount)
)

print(
    "Invalid transaction-account relationships:",
    len(invalid_transaction_accounts)
)

print(
    "Invalid account-customer relationships:",
    len(invalid_account_customer)
)

print(
    "Invalid account-branch relationships:",
    len(invalid_account_branch)
)

print(
    "High-value transactions:",
    len(high_value_transactions)
)

print(
    "Rapid transactions:",
    len(rapid_transactions)
)

print(
    "Sudden location changes:",
    len(location_changes)
)

print(
    "Customers with repeated failed transactions:",
    len(repeated_failed_transactions)
)

print(
    "Customers with unusual login devices:",
    len(unusual_login_devices)
)

print("\nCleaned Dataset Sizes:")

print("Customers:", customers.shape)
print("Accounts:", accounts.shape)
print("Transactions:", transactions.shape)
print("Loans:", loans.shape)
print("Loan Payments:", loan_payments.shape)
print("Credit Scores:", credit_scores.shape)
print("Branches:", branches.shape)
print("Complaints:", complaints.shape)
print("Login Activity:", login_activity.shape)

print("\n" + "-" * 80)

print("CLEANED DATASETS:")
print(cleaned_output_path)

print(
    "Total Cleaned Files:",
    len(cleaned_files)
)

print("\nDATA QUALITY REPORTS:")
print(report_output_path)

print(
    "Total Report Files:",
    len(quality_reports)
)

print(
    "\nTotal Files Created:",
    len(cleaned_files) + len(quality_reports)
)

print("\n" + "=" * 80)
print("PART 1 COMPLETED SUCCESSFULLY")
print("=" * 80)