# Interview walkthrough: Finance KPI & Budget vs Actual Analytics

Use this only after you have read the code and can explain each step. This is a portfolio project built on generated synthetic data, not a real company assignment.

## 60-second explanation
I built a finance performance analytics example around monthly actuals versus budget. The data is modeled at month × region × department × account grain, with separate account, department, and region dimensions. SQL produces monthly P&L and variance views; Python validates keys and values, computes revenue, COGS, operating expenses, operating profit, margin, and variance, then exports charts and summary files. I designed an Infor Birst implementation guide that maps the model to a Finance Performance subject area, KPI dashlets, Visualizer reports, and dashboard filters. The sample data is synthetic; I have not represented the dashboard as deployed in Birst unless I actually build and test it there.

## Questions to prepare for

### Why use a fact table and dimensions?
The fact table stores numeric budget/actual measures at a defined grain. Dimensions provide readable account, department, and region attributes for filtering and grouping. This keeps the model understandable for reporting and reduces the chance of mixing unrelated levels of detail.

### What is the grain?
One row per month_start × region_id × department_id × account_id. The automated test checks uniqueness of this key.

### How do you define variance?
Variance = Actual − Budget. Positive revenue variance generally indicates revenue above budget; positive expense variance generally indicates spending above budget and can be unfavorable. For overall performance, I compare operating-profit variance.

### How is operating profit calculated?
Operating Profit = Revenue − COGS − Operating Expenses. Operating Margin % = Operating Profit ÷ Revenue × 100, with zero revenue handled to avoid division errors.

### What quality checks are included?
Unique grain, valid foreign keys, 12 monthly periods, nonnegative monetary inputs, and account-type completeness. SQL includes duplicate-grain and missing-dimension checks for reconciliation after import.

### What would you do before production use?
Confirm account mapping with Finance, review actual budget methodology, validate currency and accounting period rules, handle accruals/adjustments and fiscal calendars, protect sensitive finance data, and reconcile every KPI with the approved source system. The current model intentionally does not implement these company-specific controls.

### How does this connect to Infor Birst?
The build guide covers fact/dimension joins, user-friendly subject-area attributes and measures, KPI dashlets, Visualizer reports, standard filters, and reconciliations. It is a build plan, not proof of a deployed Birst dashboard.
