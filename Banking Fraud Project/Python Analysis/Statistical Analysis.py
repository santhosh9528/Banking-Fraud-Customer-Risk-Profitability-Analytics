import pandas as pd
import numpy as np
import os

from scipy import stats

# ============================================================
# BANKING FRAUD, CUSTOMER RISK & PROFITABILITY ANALYTICS
# PART 6 - STATISTICAL ANALYSIS
# ============================================================

print("=" * 90)
print("PART 6 - STATISTICAL ANALYSIS")
print("=" * 90)

# ============================================================
# 1. PATHS
# ============================================================

cleaned_path = r"C:\Users\Hooooo\Documents\Excel\Banking Fraud Project\Cleaned Data"

loan_risk_path = r"C:\Users\Hooooo\Documents\Excel\Banking Fraud Project\Loan Risk Analysis"

output_path = r"C:\Users\Hooooo\Documents\Excel\Banking Fraud Project\Statistical Analysis"

os.makedirs(output_path, exist_ok=True)

# ============================================================
# 2. LOAD DATA
# ============================================================

transactions = pd.read_csv(
    os.path.join(
        cleaned_path,
        "transactions_cleaned.csv"
    )
)

loan_risk = pd.read_csv(
    os.path.join(
        loan_risk_path,
        "loan_risk_analysis.csv"
    )
)

print("\nDatasets loaded successfully!")

print("Transactions:", transactions.shape)
print("Loan Risk:", loan_risk.shape)

# ============================================================
# 3. PREPARE DEFAULT VARIABLE
# ============================================================

loan_risk["default_status"] = (
    loan_risk["default_status"]
    .astype(str)
    .str.strip()
    .str.title()
)

loan_risk["default_flag"] = np.where(
    loan_risk["default_status"] == "Yes",
    1,
    0
)

# ============================================================
# 4. CORRELATION ANALYSIS
# ============================================================

print("\n" + "=" * 90)
print("1. CORRELATION ANALYSIS")
print("=" * 90)

correlation_columns = [
    "credit_score",
    "annual_income",
    "loan_amount",
    "interest_rate_pct",
    "outstanding_balance",
    "days_past_due",
    "repayment_rate_pct",
    "late_payment_rate_pct",
    "loan_risk_score",
    "default_flag"
]

available_columns = [
    col for col in correlation_columns
    if col in loan_risk.columns
]

correlation_matrix = (
    loan_risk[available_columns]
    .corr(numeric_only=True)
)

print("\nCorrelation Matrix:")
print(correlation_matrix.round(3))

print("\nCorrelation With Loan Default:")

default_correlations = (
    correlation_matrix["default_flag"]
    .sort_values()
)

print(default_correlations)

# ============================================================
# 5. CREDIT SCORE VS DEFAULT
# ============================================================

print("\n" + "=" * 90)
print("2. CREDIT SCORE VS LOAN DEFAULT")
print("=" * 90)

default_credit_scores = (
    loan_risk.loc[
        loan_risk["default_flag"] == 1,
        "credit_score"
    ]
    .dropna()
)

non_default_credit_scores = (
    loan_risk.loc[
        loan_risk["default_flag"] == 0,
        "credit_score"
    ]
    .dropna()
)

print(
    "Defaulted Loan Customers:",
    len(default_credit_scores)
)

print(
    "Non-Default Customers:",
    len(non_default_credit_scores)
)

print(
    "Mean Credit Score - Default:",
    round(default_credit_scores.mean(), 2)
)

print(
    "Mean Credit Score - Non Default:",
    round(non_default_credit_scores.mean(), 2)
)

print(
    "Median Credit Score - Default:",
    round(default_credit_scores.median(), 2)
)

print(
    "Median Credit Score - Non Default:",
    round(non_default_credit_scores.median(), 2)
)

# ============================================================
# 6. HYPOTHESIS TEST
# ============================================================

print("\n" + "=" * 90)
print("3. HYPOTHESIS TEST - CREDIT SCORE VS DEFAULT")
print("=" * 90)

print("""
H0: There is no statistically significant difference in
    credit scores between defaulted and non-defaulted customers.

H1: There is a statistically significant difference in
    credit scores between defaulted and non-defaulted customers.
""")

t_statistic, p_value = stats.ttest_ind(
    default_credit_scores,
    non_default_credit_scores,
    equal_var=False,
    nan_policy="omit"
)

print(
    "T-Statistic:",
    round(t_statistic, 4)
)

print(
    "P-Value:",
    round(p_value, 6)
)

alpha = 0.05

if p_value < alpha:

    hypothesis_result = (
        "Reject H0 - Credit score has a statistically "
        "significant relationship with loan default."
    )

else:

    hypothesis_result = (
        "Fail to reject H0 - Credit score does not show "
        "a statistically significant relationship with loan default."
    )

print("\nConclusion:")
print(hypothesis_result)

# ============================================================
# 7. POINT-BISERIAL CORRELATION
# ============================================================

print("\n" + "=" * 90)
print("4. POINT-BISERIAL CORRELATION")
print("=" * 90)

point_data = loan_risk[
    [
        "credit_score",
        "default_flag"
    ]
].dropna()

pb_corr, pb_pvalue = stats.pointbiserialr(
    point_data["default_flag"],
    point_data["credit_score"]
)

print(
    "Point-Biserial Correlation:",
    round(pb_corr, 4)
)

print(
    "P-Value:",
    round(pb_pvalue, 6)
)

if pb_corr < 0:
    print(
        "Interpretation: Higher credit score is associated "
        "with lower probability of default."
    )
else:
    print(
        "Interpretation: Higher credit score is associated "
        "with higher probability of default."
    )

# ============================================================
# 8. 95% CONFIDENCE INTERVAL
# ============================================================

print("\n" + "=" * 90)
print("5. 95% CONFIDENCE INTERVALS")
print("=" * 90)


def confidence_interval(data, confidence=0.95):

    data = pd.Series(data).dropna()

    n = len(data)

    mean = data.mean()

    std_error = stats.sem(data)

    margin_error = (
        stats.t.ppf(
            (1 + confidence) / 2,
            n - 1
        )
        * std_error
    )

    lower = mean - margin_error
    upper = mean + margin_error

    return mean, lower, upper


default_mean, default_lower, default_upper = (
    confidence_interval(
        default_credit_scores
    )
)

nondefault_mean, nondefault_lower, nondefault_upper = (
    confidence_interval(
        non_default_credit_scores
    )
)

print("\nDefaulted Customers:")
print(
    "Mean Credit Score:",
    round(default_mean, 2)
)
print(
    "95% CI:",
    round(default_lower, 2),
    "to",
    round(default_upper, 2)
)

print("\nNon-Defaulted Customers:")
print(
    "Mean Credit Score:",
    round(nondefault_mean, 2)
)
print(
    "95% CI:",
    round(nondefault_lower, 2),
    "to",
    round(nondefault_upper, 2)
)

# ============================================================
# 9. REGRESSION ANALYSIS
# ============================================================

print("\n" + "=" * 90)
print("6. REGRESSION ANALYSIS")
print("=" * 90)

regression_columns = [
    "credit_score",
    "annual_income",
    "loan_amount",
    "interest_rate_pct",
    "days_past_due",
    "repayment_rate_pct",
    "default_flag"
]

regression_data = (
    loan_risk[regression_columns]
    .replace(
        [np.inf, -np.inf],
        np.nan
    )
    .dropna()
    .copy()
)

X_columns = [
    "credit_score",
    "annual_income",
    "loan_amount",
    "interest_rate_pct",
    "days_past_due",
    "repayment_rate_pct"
]

# Standardize X variables
X_standardized = (
    regression_data[X_columns]
    -
    regression_data[X_columns].mean()
) / regression_data[X_columns].std()

X = X_standardized.to_numpy()

y = regression_data[
    "default_flag"
].to_numpy()

# Add intercept
X_with_intercept = np.column_stack(
    [
        np.ones(len(X)),
        X
    ]
)

coefficients = np.linalg.lstsq(
    X_with_intercept,
    y,
    rcond=None
)[0]

predicted = (
    X_with_intercept
    @ coefficients
)

ss_residual = np.sum(
    (y - predicted) ** 2
)

ss_total = np.sum(
    (y - np.mean(y)) ** 2
)

r_squared = (
    1 - ss_residual / ss_total
)

regression_results = pd.DataFrame(
    {
        "Variable": [
            "Intercept"
        ] + X_columns,

        "Coefficient": coefficients
    }
)

print(
    "\nLinear Probability Regression Coefficients:"
)

print(regression_results)

print(
    "\nR-Squared:",
    round(r_squared, 4)
)

print("""
Regression interpretation:
Positive coefficient = variable is associated with
higher default probability.

Negative coefficient = variable is associated with
lower default probability.
""")

# ============================================================
# 10. OUTLIER DETECTION - LOAN AMOUNT
# ============================================================

print("\n" + "=" * 90)
print("7. OUTLIER DETECTION")
print("=" * 90)


def detect_iqr_outliers(df, column):

    valid = df[column].dropna()

    q1 = valid.quantile(0.25)
    q3 = valid.quantile(0.75)

    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    outliers = df[
        (df[column] < lower)
        |
        (df[column] > upper)
    ].copy()

    return q1, q3, lower, upper, outliers


loan_q1, loan_q3, loan_lower, loan_upper, loan_outliers = (
    detect_iqr_outliers(
        loan_risk,
        "loan_amount"
    )
)

print("\nLoan Amount Outliers:")

print("Q1:", round(loan_q1, 2))
print("Q3:", round(loan_q3, 2))
print("Lower Bound:", round(loan_lower, 2))
print("Upper Bound:", round(loan_upper, 2))
print("Outlier Count:", len(loan_outliers))

# ============================================================
# 11. TRANSACTION AMOUNT OUTLIERS
# ============================================================

transaction_q1, transaction_q3, transaction_lower, transaction_upper, transaction_outliers = (
    detect_iqr_outliers(
        transactions,
        "transaction_amount"
    )
)

print("\nTransaction Amount Outliers:")

print(
    "Upper Bound:",
    round(transaction_upper, 2)
)

print(
    "Outlier Count:",
    len(transaction_outliers)
)

# ============================================================
# 12. CREDIT SCORE OUTLIERS
# ============================================================

credit_q1, credit_q3, credit_lower, credit_upper, credit_outliers = (
    detect_iqr_outliers(
        loan_risk,
        "credit_score"
    )
)

print("\nCredit Score Statistical Outliers:")

print(
    "Count:",
    len(credit_outliers)
)

# ============================================================
# 13. DEFAULT RATE CONFIDENCE INTERVAL
# ============================================================

print("\n" + "=" * 90)
print("8. DEFAULT RATE 95% CONFIDENCE INTERVAL")
print("=" * 90)

n = len(loan_risk)

default_rate = (
    loan_risk["default_flag"].mean()
)

default_se = np.sqrt(
    default_rate
    *
    (1 - default_rate)
    /
    n
)

default_ci_lower = (
    default_rate
    -
    1.96 * default_se
)

default_ci_upper = (
    default_rate
    +
    1.96 * default_se
)

print(
    "Observed Default Rate:",
    round(default_rate * 100, 2),
    "%"
)

print(
    "95% Confidence Interval:",
    round(default_ci_lower * 100, 2),
    "%",
    "to",
    round(default_ci_upper * 100, 2),
    "%"
)

# ============================================================
# 14. STATISTICAL SUMMARY TABLE
# ============================================================

statistics_summary = pd.DataFrame(
    {
        "Metric": [
            "Default Credit Score Mean",
            "Non Default Credit Score Mean",
            "T Statistic",
            "T Test P Value",
            "Point Biserial Correlation",
            "Point Biserial P Value",
            "Regression R Squared",
            "Observed Default Rate %",
            "Default Rate CI Lower %",
            "Default Rate CI Upper %",
            "Loan Amount Outliers",
            "Transaction Amount Outliers"
        ],

        "Value": [
            default_credit_scores.mean(),
            non_default_credit_scores.mean(),
            t_statistic,
            p_value,
            pb_corr,
            pb_pvalue,
            r_squared,
            default_rate * 100,
            default_ci_lower * 100,
            default_ci_upper * 100,
            len(loan_outliers),
            len(transaction_outliers)
        ]
    }
)

# ============================================================
# 15. SAVE OUTPUTS
# ============================================================

print("\n" + "=" * 90)
print("SAVING STATISTICAL ANALYSIS RESULTS")
print("=" * 90)

correlation_matrix.to_csv(
    os.path.join(
        output_path,
        "correlation_matrix.csv"
    )
)

regression_results.to_csv(
    os.path.join(
        output_path,
        "regression_results.csv"
    ),
    index=False
)

statistics_summary.to_csv(
    os.path.join(
        output_path,
        "statistical_summary.csv"
    ),
    index=False
)

loan_outliers.to_csv(
    os.path.join(
        output_path,
        "loan_amount_outliers.csv"
    ),
    index=False
)

transaction_outliers.to_csv(
    os.path.join(
        output_path,
        "transaction_amount_outliers.csv"
    ),
    index=False
)

credit_outliers.to_csv(
    os.path.join(
        output_path,
        "credit_score_outliers.csv"
    ),
    index=False
)

# ============================================================
# 16. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 90)
print("PART 6 - STATISTICAL ANALYSIS SUMMARY")
print("=" * 90)

print(
    "\nDefault Customer Average Credit Score:",
    round(default_credit_scores.mean(), 2)
)

print(
    "Non-Default Customer Average Credit Score:",
    round(non_default_credit_scores.mean(), 2)
)

print(
    "T-Test P-Value:",
    round(p_value, 6)
)

print(
    "Point-Biserial Correlation:",
    round(pb_corr, 4)
)

print(
    "Regression R-Squared:",
    round(r_squared, 4)
)

print(
    "Default Rate:",
    round(default_rate * 100, 2),
    "%"
)

print(
    "Default Rate 95% CI:",
    round(default_ci_lower * 100, 2),
    "%",
    "to",
    round(default_ci_upper * 100, 2),
    "%"
)

print(
    "\nHypothesis Test Result:"
)

print(hypothesis_result)

print("\nFiles saved to:")
print(output_path)

print("\n" + "=" * 90)
print("PART 6 - STATISTICAL ANALYSIS COMPLETED SUCCESSFULLY")
print("=" * 90)