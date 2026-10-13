# KPI Dictionary

| KPI | Definition | Interpretation |
|---|---|---|
| Actual Revenue | Sum of actual amounts where account type = Revenue | Revenue achieved in the selected period |
| Budget Revenue | Sum of budget amounts where account type = Revenue | Planned revenue |
| Revenue Variance | Actual revenue − budget revenue | Positive is generally favourable |
| Actual COGS | Sum of actual amounts where account type = COGS | Actual cost of goods sold |
| Actual Operating Expense | Sum of actual amounts where account type = Operating Expense | Actual operating expense |
| Actual Operating Profit | Actual revenue − actual COGS − actual operating expense | Profit under this simplified model |
| Operating-Profit Variance | Actual operating profit − budget operating profit | Positive is generally favourable |
| Operating Margin | Operating profit ÷ revenue × 100 | Profitability relative to revenue |
| Expense Variance | Actual expense − budget expense | Positive is generally unfavourable (overspend) |
| Revenue Variance % | Revenue variance ÷ budget revenue × 100 | Relative gap vs plan |

## Important modelling notes
- Dataset is synthetic and intended for learning.
- All amounts are non-negative line items; profit is derived from account classifications.
- Budget and actual must be aggregated at compatible grains before comparing.
- For zero budgets, variance percentage should be undefined/null rather than infinite.
- Account-type sign logic must be applied explicitly; do not apply one generic favourable/unfavourable rule to every KPI.
