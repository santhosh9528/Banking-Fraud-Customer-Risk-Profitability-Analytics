# 🏦 Banking Fraud, Customer Risk & Profitability Analytics

End-to-end banking analytics project using **Python, MySQL, Statistics, and Power BI** to analyze fraud risk, loan defaults, customer profitability, and banking performance.

---

## 📊 Power BI Dashboards

### Executive Dashboard

![Executive Dashboard](Banking%20Fraud%20Project/Power%20Bi/Dashboards%20Screenshots/Executive%20Dashboard.png)

The Executive Dashboard provides an overview of customer activity, transaction performance, loan portfolio, default rate, fraud exposure, and customer profitability.

---

### Fraud Analysis Dashboard

![Fraud Analysis Dashboard](/Power%20Bi/Dashboards%20Screenshots/Fraud%20Analysis.png)

The Fraud Analysis Dashboard focuses on suspicious transactions, fraud risk scores, branch-level fraud activity, and customer risk segments.

---

### Loan Analysis Dashboard

![Loan Analysis Dashboard](./Power%20Bi/Dashboards%20Screenshots/Loan%20Analysis.png)

The Loan Analysis Dashboard provides insights into loan portfolio performance, default rates, credit score distribution, loan risk segments, and branch-level loan risk.

---

## 🎯 Project Objectives

- Detect suspicious and fraudulent transactions
- Identify high-risk customers
- Analyze loan defaults and repayment behavior
- Evaluate customer profitability
- Identify high-value and high-risk customers
- Analyze branch-level banking performance
- Build interactive Power BI dashboards

---

## 🛠️ Tools & Technologies

- Python
- Pandas
- NumPy
- SciPy
- MySQL
- SQL
- Power BI
- DAX
- Statistics

---

## 🔍 Fraud Analysis

The fraud investigation analyzed:

- Rapid repeated transactions
- Unusual transaction amounts
- Sudden location changes
- Multiple devices
- Unusual merchant activity
- Repeated failed transactions
- Suspicious login activity
- High-value transactions after dormant periods

### Key Fraud Results

- Suspicious Transactions: **280**
- Confirmed Fraud Transactions: **140**
- High/Critical Fraud-Risk Customers: **114**
- Rapid Transactions: **81**
- Sudden Location Changes: **25**
- Transaction Amount Outliers: **2,199**

---

## 💳 Loan Risk Analysis

Loan risk was analyzed using credit scores, income, loan amounts, interest rates, repayment history, outstanding balances, and days past due.

### Key Loan Results

- Valid Loans: **646**
- Defaulted Loans: **140**
- Default Rate: **21.67%**
- High/Critical Risk Loans: **205**
- Highest Risk Branch: **B013 – Mumbai Branch 2**
- B013 Default Rate: **39.13%**

---

## 💰 Customer Profitability

Customer profitability was modeled using transaction fee revenue, estimated annual loan interest revenue, transaction operational costs, account service costs, and complaint service costs.

### Key Results

- Modeled Customer Revenue: **₹29.40M**
- Modeled Operational Cost: **₹2.96M**
- Modeled Customer Profit: **₹26.45M**
- Profitable Customers: **479**
- Loss-Making Customers: **520**
- High Value – High Risk Customers: **139**

---

## 📈 Statistical Analysis

Statistical techniques used:

- Correlation Analysis
- Hypothesis Testing
- Confidence Intervals
- Regression Analysis
- Point-Biserial Correlation
- Outlier Detection

### Credit Score vs Loan Default

- Defaulted Customer Average Credit Score: **677.80**
- Non-Default Customer Average Credit Score: **699.52**
- T-Statistic: **-3.3091**
- P-Value: **0.001083**

Since the p-value is below 0.05, the analysis found a statistically significant relationship between credit score and loan default in the dataset.

---

## 💡 Key Business Insights

- **280** transactions were classified as High/Critical fraud risk.
- All **140 synthetic confirmed fraud transactions** were captured by the High/Critical fraud-risk criteria.
- **114** customers were classified as High/Critical fraud risk.
- Overall loan default rate was **21.67%**.
- **205** loans were classified as High/Critical risk.
- Defaulted customers had lower average credit scores than non-defaulted customers.
- **520** customers were loss-making under the profitability model.
- **139** customers were classified as High Value – High Risk.

---

## 📌 Business Recommendations

- Implement real-time fraud monitoring.
- Use multi-factor fraud risk scoring.
- Monitor High/Critical risk customers closely.
- Build loan early-warning alerts using repayment behavior.
- Review branches with high loan default rates.
- Strengthen underwriting for high-risk loan segments.
- Protect High Value – High Risk customers using enhanced monitoring.
- Improve profitability of loss-making customer segments.

---

## 📂 Project Structure

```text
Banking Fraud Project/
│
├── Rawdata/
├── Cleaned Data/
├── Data Quality report/
├── Python Analysis/
├── SQL/
├── Fraud Analysis/
├── Loan Risk Analysis/
├── Customer Profitability/
├── Statistical Analysis/
├── Power Bi/
│   ├── Banking Analytics.pbix
│   └── Dashboards Screenshots/
│       ├── Executive Dashboard.png
│       ├── Fraud Analysis.png
│       └── Loan Analysis.png
├── Report/
└── README.md
