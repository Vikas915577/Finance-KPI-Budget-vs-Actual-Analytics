# Infor Birst Model & Dashboard Build Guide — Finance KPI Analytics

## What this is / is not
This is a **portfolio project using generated synthetic finance data**. It includes a Birst-oriented model and dashboard build plan. It does **not** claim a live dashboard has already been configured in an Infor Birst tenant.

## Suggested model
- `fact_finance_monthly`: one row per month × region × department × account, with budget and actual amounts.
- `dim_account`: account name, account type and financial statement line.
- `dim_department`: reporting department.
- `dim_region`: reporting region.

The generated data has 1,680 fact rows across 12 months, 4 regions, 5 departments, and 7 accounts. Currency is labelled USD for demo consistency; amounts are synthetic and not based on a real company's books.

## Joins
- `fact_finance_monthly.account_id` → `dim_account.account_id`
- `fact_finance_monthly.department_id` → `dim_department.department_id`
- `fact_finance_monthly.region_id` → `dim_region.region_id`
- Use `month_start` as the time attribute; ensure it is interpreted as a date.
- Preserve fact grain. Avoid joining unrelated fact tables directly.

## Subject area: Finance Performance
### Suggested attributes
Month, Region, Department, Account Name, Account Type, Financial Statement Line, Currency Code.
### Suggested measures
- Actual Amount = SUM(actual_amount)
- Budget Amount = SUM(budget_amount)
- Variance Amount = SUM(actual_amount) - SUM(budget_amount)
- Variance % = 100 × variance / budget, with zero-budget handling
- Actual Revenue = sum of actual amounts for Revenue accounts
- Budget Revenue = sum of budget amounts for Revenue accounts
- Actual COGS / Budget COGS
- Actual Operating Expense / Budget Operating Expense
- Actual Operating Profit = Revenue − COGS − Operating Expenses
- Operating Profit Variance = Actual Operating Profit − Budget Operating Profit
- Actual Operating Margin % = Actual Operating Profit / Actual Revenue × 100

**Interpretation caution:** Variance = Actual − Budget. Positive revenue variance is generally favorable; positive expense variance is generally unfavorable. Operating profit variance is the more comparable combined profitability KPI. Don't treat every positive variance as good.

## Dashboard plan
### Page 1 — Executive Finance Overview
KPI dashlets: Actual Revenue, Revenue Variance %, Actual Operating Profit, Operating Profit Variance, Actual Operating Margin %.
Charts: monthly Actual vs Budget Revenue; monthly Operating Profit Actual vs Budget; filterable summary by Region.
Filters: Month, Region, Department.

### Page 2 — Department Performance
Chart: Operating Profit Variance by Department.
Table: Actual Revenue, Budget Revenue, Actual Operating Expenses, Budget Operating Expenses, Actual Operating Profit, Budget Operating Profit, Operating Profit Variance, Actual Operating Margin.
Filters: Month, Region, Department.

### Page 3 — Expense Control
Chart: expense variance by account; table of monthly expense variance by account and department.
Add explanatory text: "Expense variance = Actual expense − Budget expense; positive values indicate spend above budget."
Filters: Month, Region, Department, Account.

## Recommended implementation sequence
1. Work in a personal practice/demo space. Never use private employer/client financial data.
2. Import the four synthetic CSV files in `data/synthetic/`.
3. Confirm date/decimal/string data types; set amount fields as numeric and `month_start` as a date.
4. Define joins and validate the expected fact row count of 1,680 after joins.
5. Define friendly labels and a custom **Finance Performance** subject area with only relevant attributes and measures.
6. Build a small set of Visualizer reports first: Revenue Actual vs Budget by Month, Operating Profit Variance by Department, Expense Variance by Account, and a detailed reconciliation table.
7. Compose dashboard pages and add filter cards and KPI dashlets. In Birst Dashboards, reports, filters and KPIs can be assembled on pages; use official documentation below as the UI reference.
8. Reconcile Birst totals against `outputs/executive_kpis.csv` and monthly results against `outputs/monthly_pnl_summary.csv`.
9. Test each filter combination, zero-budget logic, currency label, date sorting, and export behavior.
10. Only after you personally implement and test the dashboard, capture screenshots and update the README to state exactly what you built.

## Reconciliation checks
- Loaded fact row count should be 1,680.
- Use the same filters/time range in Birst and generated CSV outputs when comparing totals.
- Actual and budget amounts should reconcile by account type and month.
- Operating Profit = Revenue − COGS − Operating Expenses.
- Operating Profit Variance = Actual Operating Profit − Budget Operating Profit.

## Official Infor references
- Dashboards and KPI/report dashlets: https://docs.infor.com/birst/2025.x/en-us/birstolh/dashboards_user/ifj1655271234451.html
- Visualizer filters: https://docs.infor.com/birst/2025.x/en-us/birstolh/reports_user/xah1655271135431.html
- Managing subject areas: https://docs.infor.com/birst/2026.x/en-us/birstolh/admin/adminsubjectarea.html
- BQL basics (attributes, measures, subject areas): https://docs.infor.com/birst/latest/en-us/birstolh/birstug_bqlref/acc1717688368889.html
