-- Finance KPI analysis queries (PostgreSQL)
-- Convention: variance = Actual - Budget. Revenue positive variance is generally favorable;
-- expense positive variance is generally unfavorable. Assess line type before interpreting.

-- Q1. Monthly revenue, gross profit and operating profit actual vs budget
WITH lines AS (
  SELECT f.month_start, a.account_type,
         SUM(f.actual_amount) AS actual_amount,
         SUM(f.budget_amount) AS budget_amount
  FROM fact_finance_monthly f JOIN dim_account a USING (account_id)
  GROUP BY f.month_start, a.account_type
), monthly AS (
  SELECT month_start,
    SUM(CASE WHEN account_type='Revenue' THEN actual_amount ELSE 0 END) AS actual_revenue,
    SUM(CASE WHEN account_type='Revenue' THEN budget_amount ELSE 0 END) AS budget_revenue,
    SUM(CASE WHEN account_type='COGS' THEN actual_amount ELSE 0 END) AS actual_cogs,
    SUM(CASE WHEN account_type='COGS' THEN budget_amount ELSE 0 END) AS budget_cogs,
    SUM(CASE WHEN account_type='Operating Expense' THEN actual_amount ELSE 0 END) AS actual_opex,
    SUM(CASE WHEN account_type='Operating Expense' THEN budget_amount ELSE 0 END) AS budget_opex
  FROM lines GROUP BY month_start
)
SELECT *,
  actual_revenue-actual_cogs AS actual_gross_profit,
  budget_revenue-budget_cogs AS budget_gross_profit,
  actual_revenue-actual_cogs-actual_opex AS actual_operating_profit,
  budget_revenue-budget_cogs-budget_opex AS budget_operating_profit,
  (actual_revenue-actual_cogs-actual_opex)-(budget_revenue-budget_cogs-budget_opex) AS operating_profit_variance,
  100.0*(actual_revenue-actual_cogs-actual_opex)/NULLIF(actual_revenue,0) AS actual_operating_margin_pct
FROM monthly ORDER BY month_start;

-- Q2. Operating-profit variance by department and region
WITH p AS (
  SELECT f.department_id, d.department_name, f.region_id, r.region_name,
    SUM(CASE WHEN a.account_type='Revenue' THEN f.actual_amount WHEN a.account_type IN ('COGS','Operating Expense') THEN -f.actual_amount ELSE 0 END) AS actual_operating_profit,
    SUM(CASE WHEN a.account_type='Revenue' THEN f.budget_amount WHEN a.account_type IN ('COGS','Operating Expense') THEN -f.budget_amount ELSE 0 END) AS budget_operating_profit
  FROM fact_finance_monthly f JOIN dim_account a USING(account_id)
  JOIN dim_department d USING(department_id) JOIN dim_region r USING(region_id)
  GROUP BY f.department_id,d.department_name,f.region_id,r.region_name
)
SELECT *, actual_operating_profit-budget_operating_profit AS operating_profit_variance
FROM p ORDER BY operating_profit_variance;

-- Q3. Expense variance by account, department, and month
SELECT f.month_start, d.department_name, a.account_name,
  SUM(f.actual_amount) AS actual_expense, SUM(f.budget_amount) AS budget_expense,
  SUM(f.actual_amount)-SUM(f.budget_amount) AS expense_variance,
  100.0*(SUM(f.actual_amount)-SUM(f.budget_amount))/NULLIF(SUM(f.budget_amount),0) AS variance_pct
FROM fact_finance_monthly f JOIN dim_account a USING(account_id) JOIN dim_department d USING(department_id)
WHERE a.account_type IN ('COGS','Operating Expense')
GROUP BY f.month_start,d.department_name,a.account_name
ORDER BY expense_variance DESC;

-- Q4. Revenue performance by region
SELECT r.region_name, SUM(f.actual_amount) AS actual_revenue, SUM(f.budget_amount) AS budget_revenue,
  SUM(f.actual_amount)-SUM(f.budget_amount) AS revenue_variance,
  100.0*(SUM(f.actual_amount)-SUM(f.budget_amount))/NULLIF(SUM(f.budget_amount),0) AS revenue_variance_pct
FROM fact_finance_monthly f JOIN dim_account a USING(account_id) JOIN dim_region r USING(region_id)
WHERE a.account_type='Revenue'
GROUP BY r.region_name ORDER BY revenue_variance DESC;

-- Q5. Data quality: fact grain duplicates (should return no rows)
SELECT month_start,region_id,department_id,account_id,COUNT(*) AS record_count
FROM fact_finance_monthly GROUP BY month_start,region_id,department_id,account_id HAVING COUNT(*)>1;

-- Q6. Reconciliation: fact foreign keys missing dimension records (should return no rows)
SELECT f.* FROM fact_finance_monthly f
LEFT JOIN dim_region r USING(region_id)
LEFT JOIN dim_department d USING(department_id)
LEFT JOIN dim_account a USING(account_id)
WHERE r.region_id IS NULL OR d.department_id IS NULL OR a.account_id IS NULL;
