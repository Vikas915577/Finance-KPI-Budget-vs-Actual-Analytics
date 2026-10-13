# Infor Birst Finance Dashboard — Implementation Blueprint

**Status:** Design/portfolio blueprint. Not a claim of a deployed Birst dashboard.

## 1. Intended business outcome
Enable Finance/FP&A to answer:
1. Are revenue and operating profit above or below budget?
2. Which department, region and account explain the largest variance?
3. What should the owner investigate next?

## 2. Data model
**Fact grain:** one record per month × region × department × account.

Fact fields:
- `month_start`
- `region_id`
- `department_id`
- `account_id`
- `budget_amount`
- `actual_amount`

Dimensions:
- Account: `account_id`, `account_name`, `account_type`
- Department: `department_id`, `department_name`
- Region: `region_id`, `region_name`
- Date: derive a calendar/date dimension in the Birst model as supported by the practice-space configuration.

Keep grain explicit. Do not join a one-to-many dimension in a way that duplicates fact amounts.

## 3. Subject area and semantic layer
Create a subject area such as **Finance Performance** with friendly folders:
- Executive KPIs
- Revenue & Budget
- Cost & Expense
- Profitability
- Organization (department/region)
- Calendar

Suggested attributes:
- Month, quarter, year
- Region name
- Department name
- Account name and account type

Suggested base measures:
- Actual Amount = sum(actual_amount)
- Budget Amount = sum(budget_amount)
- Variance Amount = Actual Amount − Budget Amount (use account-aware logic for business interpretation)
- Revenue Actual/Budget: aggregate only Revenue account type
- COGS Actual/Budget: aggregate only COGS account type
- Operating Expense Actual/Budget: aggregate only Operating Expense account type
- Operating Profit Actual = Revenue Actual − COGS Actual − Operating Expense Actual
- Operating Profit Budget = Revenue Budget − COGS Budget − Operating Expense Budget
- Operating Profit Variance = Operating Profit Actual − Operating Profit Budget
- Operating Margin Actual % = Operating Profit Actual ÷ Revenue Actual
- Revenue Variance % = (Revenue Actual − Revenue Budget) ÷ Revenue Budget

**Implementation caution:** Configure these as correctly scoped Birst measures/expressions in the target space and validate them against SQL/Python. Exact expression syntax depends on the Birst model and expression context.

## 4. Dashboard layout: Display → Diagnose → Decide

### Page 1 — Executive view (DISPLAY)
Business question: **Are we on plan?**
- KPI tiles: Actual Revenue, Revenue Variance %, Operating Profit, Operating Profit Variance, Operating Margin.
- Trend: monthly actual vs budget revenue.
- Period label and shared filters.
- Short narrative showing what moved, with synthetic-data disclosure.

### Page 2 — Variance drivers (DIAGNOSE)
Business question: **Where is the gap coming from?**
- Sorted bar: operating-profit variance by department.
- Sorted bar/table: expense variance by account.
- Region comparison: revenue and operating-profit variance by region.
- Drill path: period → region → department → account.
- Display actual, budget, absolute variance and variance % side by side.

### Page 3 — Action register (DECIDE)
Business question: **What will we investigate, who owns it, and when will we check again?**
Suggested fields for a real business workflow:
- Priority / variance item
- Observed signal
- Hypothesis to validate
- Owner
- Next action
- Due date
- Status
- Next-period outcome

This register is a proposed workflow. The synthetic data does not prove the cause of a variance.

## 5. Filters and interaction
Recommended shared filters:
- Month/date range
- Region
- Department
- Account type/account

Test filter propagation across KPI tiles, trends and breakdowns. Show active filters and make clearing them easy. Use Birst Visualizer for exploratory reports and add validated reports to the dashboard; use Designer when a highly formatted/exportable report is required.

## 6. Reconciliation checklist
For at least one month and one region:
1. Compare row counts and totals to the source CSV/SQL.
2. Reconcile actual and budget revenue.
3. Reconcile COGS and operating expenses separately.
4. Recompute operating profit and operating-profit variance.
5. Test zero-budget handling and filter interactions.
6. Document discrepancies before publishing.

## 7. Build sequence
1. Import CSVs into an authorized Birst practice space.
2. Model fact/dimension relationships and date attributes.
3. Configure the Finance Performance subject area.
4. Define and test measures.
5. Build Visualizer reports and KPI tiles.
6. Assemble shared dashboard filters and the DDD page flow.
7. Reconcile against Python/SQL.
8. Ask a finance user to complete the stated user stories.
9. Publish and update portfolio evidence only after successful validation.

## Official references
- [Analytics with Birst — Infor Developer Portal](https://developer.infor.com/tutorials/analytics-with-birst)
- [Manage subject areas — Infor Birst documentation](https://docs.infor.com/birst/2026.x/en-us/birstolh/admin/adminsubjectarea.html)
- [Using Smart Insights — Infor Birst documentation](https://docs.infor.com/birst/2026.10/en-us/birstolh/dashboards_user/ill1655271262734.html)
- [Dynamic measures/dimensions through dashboard filters — Infor Developer Portal](https://developer.infor.com/tutorials/analytics/dynamically-change-measures-and-dimensions-in-a-report-using-a-dashboard-filter/)
