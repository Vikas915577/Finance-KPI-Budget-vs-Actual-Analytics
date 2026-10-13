# Finance KPI & Budget vs Actual Analytics (Infor Birst Portfolio Project)

**Project goal:** Show how a BI analyst can model finance data, compare actuals with budgets, define clear financial KPIs, validate results, and plan an **Infor Birst** dashboard.

> **Data disclosure:** All source figures are generated synthetic portfolio data, not actual company results. This repository includes a Birst model/dashboard build guide, not a live Birst deployment. Do not describe it as a real employer project.

## Business questions
1. Is monthly revenue above or below budget?
2. How do actual and budget operating profit compare?
3. Which departments show the largest operating-profit variance?
4. Which expense accounts explain above-budget spending?
5. How do revenue, operating margin, department, and region relate?

## Primary BI tool: Infor Birst
The Birst guide outlines an importable fact/dimension model, a Finance Performance subject area, KPIs, Visualizer reports, dashboard filters, and validation steps. This is aligned to Birst's documented dashboard, filter, subject-area and attribute/measure concepts. The dashboard must still be built and tested in a Birst practice space before claiming implementation.

## Tools
- **Infor Birst:** planned data model, custom subject area, KPI dashlets, Visualizer reports and dashboard filters.
- **SQL (PostgreSQL-compatible):** finance aggregations, department/region comparisons, expense variance and reconciliation checks.
- **Python:** pandas/NumPy calculations, validation, derived KPIs and charts.

## Data model and size
- `fact_finance_monthly`: one row per month × region × department × account.
- `dim_account`: Revenue, COGS and Operating Expense classification.
- `dim_department`: department labels.
- `dim_region`: region labels.

Generated fact rows: **1,680** across 12 months, 4 regions, 5 departments and 7 accounts.

## How to run
Python 3.10+ recommended. From the project root:

```bash
python -m pip install -r requirements.txt
python python/analyze_finance.py
python -m unittest discover -s tests -v
```

The analysis writes KPI and variance CSVs plus chart PNGs into `outputs/`.

## Included outputs
- `outputs/executive_kpis.csv` — executive finance metrics.
- `outputs/monthly_pnl_summary.csv` — monthly actual/budget revenue, COGS, operating expense, profit and margin.
- `outputs/department_profit_variance.csv` — operating-profit variance by department.
- `outputs/account_variance_summary.csv` — account-level budget vs actual.
- `outputs/region_revenue_variance.csv` — regional revenue performance.
- `outputs/findings.txt` — data-derived findings, explicitly labelled synthetic.
- `outputs/charts/` — four chart images.
- `birst/BIRST_FINANCE_MODEL_AND_DASHBOARD_GUIDE.md` — Birst model and build guide.

## Important interpretation rule
**Variance = Actual − Budget.** Positive revenue variance is generally favorable; positive expense variance is generally unfavorable. For overall performance, review Operating Profit Variance (actual operating profit minus budget operating profit), not one undifferentiated variance field.

## Project structure
```text
data/synthetic/   # generated finance fact and dimension CSVs
sql/              # schema, KPI queries, QA/reconciliation
python/            # reproducible analysis script
outputs/           # results and charts (regeneratable)
birst/             # Infor Birst model & dashboard implementation guide
tests/             # automated data validation tests
docs/              # project notes
```

## GitHub upload checklist
1. Create a public repository such as `finance-kpi-budget-vs-actual`.
2. Upload the **contents** of this ZIP, not only the ZIP file.
3. Ensure README renders and relative image paths (if added) work.
4. Never upload company data, access credentials, or private screenshots.
5. Build the dashboard in your own Infor Birst practice space; capture your own screenshot only after validation.
6. Add your project month/year and update the README with what you personally completed.

## Resume wording — use after reviewing and being able to explain the work
**Finance KPI & Budget vs Actual Analytics | Infor Birst, SQL, Python**
- Modeled monthly budget and actual finance data across revenue, cost of goods sold and operating expenses using fact/dimension tables.
- Analyzed revenue, operating-profit and expense variances with SQL and Python; built reproducible KPI summaries and charts from synthetic data.
- Designed an Infor Birst implementation guide covering a Finance Performance subject area, KPI tiles, Visualizer reports, dashboard filters and reconciliation checks.

Do not say you deployed a Birst dashboard unless you have built and tested it inside Birst.
