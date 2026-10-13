-- Referential-integrity checks (expected result: zero rows each).
SELECT f.account_id FROM fact_finance_monthly f LEFT JOIN dim_account d USING(account_id) WHERE d.account_id IS NULL;
SELECT f.department_id FROM fact_finance_monthly f LEFT JOIN dim_department d USING(department_id) WHERE d.department_id IS NULL;
SELECT f.region_id FROM fact_finance_monthly f LEFT JOIN dim_region d USING(region_id) WHERE d.region_id IS NULL;

-- Budget/actual variance convention used throughout this project:
-- Revenue variance = actual revenue - budget revenue (positive usually favourable).
-- Expense variance = actual expense - budget expense (positive usually unfavourable).
-- Operating-profit variance = actual operating profit - budget operating profit.
