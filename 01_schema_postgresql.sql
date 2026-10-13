-- PostgreSQL-compatible logical model for the synthetic portfolio.
CREATE TABLE dim_account (
  account_id VARCHAR(10) PRIMARY KEY,
  account_name VARCHAR(100) NOT NULL,
  account_type VARCHAR(30) NOT NULL CHECK (account_type IN ('Revenue','COGS','Operating Expense'))
);
CREATE TABLE dim_department (department_id VARCHAR(10) PRIMARY KEY, department_name VARCHAR(100) NOT NULL);
CREATE TABLE dim_region (region_id VARCHAR(10) PRIMARY KEY, region_name VARCHAR(100) NOT NULL);
CREATE TABLE fact_finance_monthly (
  month_start DATE NOT NULL,
  region_id VARCHAR(10) NOT NULL REFERENCES dim_region(region_id),
  department_id VARCHAR(10) NOT NULL REFERENCES dim_department(department_id),
  account_id VARCHAR(10) NOT NULL REFERENCES dim_account(account_id),
  budget_amount NUMERIC(14,2) NOT NULL CHECK (budget_amount >= 0),
  actual_amount NUMERIC(14,2) NOT NULL CHECK (actual_amount >= 0),
  PRIMARY KEY (month_start, region_id, department_id, account_id)
);
-- Load dimension CSVs before fact_finance_monthly.csv.
