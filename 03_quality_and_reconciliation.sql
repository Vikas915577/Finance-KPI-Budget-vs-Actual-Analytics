-- Basic checks before interpreting budget variance
-- 1) Check total fact row count and loaded month range
SELECT COUNT(*) AS row_count, MIN(month_start) AS first_month, MAX(month_start) AS last_month FROM fact_finance_monthly;
-- 2) Validate one currency per report slice (starter file uses USD consistently)
SELECT currency_code, COUNT(*) FROM fact_finance_monthly GROUP BY currency_code;
-- 3) Compare source amounts with aggregated output before publishing dashboard.
SELECT a.account_type, SUM(f.actual_amount) AS actual, SUM(f.budget_amount) AS budget
FROM fact_finance_monthly f JOIN dim_account a USING(account_id) GROUP BY a.account_type;
-- 4) Check for null or negative financial values
SELECT * FROM fact_finance_monthly WHERE month_start IS NULL OR budget_amount IS NULL OR actual_amount IS NULL OR budget_amount<0 OR actual_amount<0;
