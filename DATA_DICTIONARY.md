# Data dictionary — synthetic finance data

All values in `data/synthetic/` are generated for portfolio practice. They are not real financial statements or employer/client data. USD is a sample currency label only.

## `dim_account.csv`
- `account_id`: account code.
- `account_name`: readable account name.
- `account_type`: Revenue, COGS, or Operating Expense.
- `financial_line`: reporting line label.
- `is_expense`: whether account is an expense in this simplified model.

## `dim_department.csv`
Unique department id and display name.

## `dim_region.csv`
Unique region id and display name.

## `fact_finance_monthly.csv`
One row per month × region × department × account.
- `month_start`: first day of the reporting month.
- `region_id`, `department_id`, `account_id`: dimension keys.
- `budget_amount`, `actual_amount`: non-negative demo values.
- `currency_code`: USD demo label.

## Variance convention
`Variance = Actual - Budget`. For revenue, positive variance generally indicates above-budget revenue. For expenses, positive variance generally indicates overspend. For combined profitability, use Operating Profit Variance.
