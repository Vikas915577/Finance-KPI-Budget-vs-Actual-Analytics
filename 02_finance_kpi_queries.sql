-- 1) Monthly revenue: display the gap against plan.
SELECT f.month_start,
       SUM(CASE WHEN a.account_type='Revenue' THEN f.actual_amount ELSE 0 END) AS actual_revenue,
       SUM(CASE WHEN a.account_type='Revenue' THEN f.budget_amount ELSE 0 END) AS budget_revenue,
       SUM(CASE WHEN a.account_type='Revenue' THEN f.actual_amount-f.budget_amount ELSE 0 END) AS revenue_variance
FROM fact_finance_monthly f JOIN dim_account a USING(account_id)
GROUP BY f.month_start ORDER BY f.month_start;

-- 2) Operating profit variance by department: diagnose where the gap sits.
SELECT d.department_name,
       SUM(CASE WHEN a.account_type='Revenue' THEN f.actual_amount
                WHEN a.account_type IN ('COGS','Operating Expense') THEN -f.actual_amount ELSE 0 END) AS actual_operating_profit,
       SUM(CASE WHEN a.account_type='Revenue' THEN f.budget_amount
                WHEN a.account_type IN ('COGS','Operating Expense') THEN -f.budget_amount ELSE 0 END) AS budget_operating_profit,
       SUM(CASE WHEN a.account_type='Revenue' THEN f.actual_amount-f.budget_amount
                ELSE f.budget_amount-f.actual_amount END) AS operating_profit_variance
FROM fact_finance_monthly f JOIN dim_account a USING(account_id)
JOIN dim_department d USING(department_id)
GROUP BY d.department_name ORDER BY operating_profit_variance;

-- 3) Expense account overspend. Positive variance = actual expense above budget.
SELECT a.account_name, SUM(f.actual_amount) AS actual_expense,
       SUM(f.budget_amount) AS budget_expense,
       SUM(f.actual_amount-f.budget_amount) AS expense_variance
FROM fact_finance_monthly f JOIN dim_account a USING(account_id)
WHERE a.account_type IN ('COGS','Operating Expense')
GROUP BY a.account_name ORDER BY expense_variance DESC;

-- 4) Data-quality: fact grain must be unique (expected no rows).
SELECT month_start,region_id,department_id,account_id,COUNT(*) AS row_count
FROM fact_finance_monthly
GROUP BY month_start,region_id,department_id,account_id HAVING COUNT(*)>1;

-- 5) Reconciliation: monthly totals must reconcile to source rows.
SELECT month_start, COUNT(*) AS fact_rows,
       SUM(actual_amount) AS actual_all_accounts,
       SUM(budget_amount) AS budget_all_accounts
FROM fact_finance_monthly GROUP BY month_start ORDER BY month_start;
