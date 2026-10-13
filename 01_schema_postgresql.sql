-- Finance KPI & Budget vs Actual Analytics — PostgreSQL schema
-- Portfolio demonstration only. All source records are synthetic.
CREATE TABLE dim_region (
  region_id VARCHAR(20) PRIMARY KEY,
  region_name VARCHAR(80) NOT NULL
);
CREATE TABLE dim_department (
  department_id VARCHAR(20) PRIMARY KEY,
  department_name VARCHAR(100) NOT NULL
);
CREATE TABLE dim_account (
  account_id VARCHAR(10) PRIMARY KEY,
  account_name VARCHAR(120) NOT NULL,
  account_type VARCHAR(40) NOT NULL CHECK (account_type IN ('Revenue','COGS','Operating Expense')),
  financial_line VARCHAR(80) NOT NULL,
  is_expense BOOLEAN NOT NULL
);
CREATE TABLE fact_finance_monthly (
  month_start DATE NOT NULL,
  region_id VARCHAR(20) NOT NULL REFERENCES dim_region(region_id),
  department_id VARCHAR(20) NOT NULL REFERENCES dim_department(department_id),
  account_id VARCHAR(10) NOT NULL REFERENCES dim_account(account_id),
  budget_amount NUMERIC(16,2) NOT NULL CHECK (budget_amount >= 0),
  actual_amount NUMERIC(16,2) NOT NULL CHECK (actual_amount >= 0),
  currency_code CHAR(3) NOT NULL DEFAULT 'USD',
  PRIMARY KEY (month_start, region_id, department_id, account_id)
);
