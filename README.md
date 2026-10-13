# Finance KPI & Budget vs Actual Analytics
### Infor Birst • SQL • Python • Display → Diagnose → Decide

> **Data disclosure:** This is a portfolio case study built on deterministic synthetic data. It is not an employer project, and the repository does not claim that a live Infor Birst dashboard has been deployed.

## Executive question
**Where are actual revenue and operating profit deviating from budget, what is driving the gap, and what should the finance owner investigate next?**

## Decision-first dashboard design: Display → Diagnose → Decide (DDD)
1. **Display — What happened?** Actual vs budget revenue, operating profit, operating margin, variance and monthly trend.
2. **Diagnose — Where is the gap?** Department, region and account breakdowns; identify the largest variances and drill to the relevant account/period.
3. **Decide — What should happen next?** Assign a variance owner, validate price/volume/timing/coding, agree a corrective action and due date, then monitor the next period. The data flags investigation priorities; it does not prove root cause by itself.

## Dashboard preview

The static dashboard is self-contained, with KPI cards and four data-derived SVG charts. The screenshots below were captured during mobile and desktop smoke testing.

![Desktop executive snapshot](docs/screenshots/desktop-executive-snapshot.png)

![Desktop variance-driver charts](docs/screenshots/desktop-variance-charts.png)

[Open the mobile chart preview](docs/screenshots/mobile-variance-charts.png)

## Business user stories
- **Finance Director:** As a Finance Director, I want actual vs budget revenue, operating profit and margin at a glance, so I can see whether the business is on plan and focus the monthly review.
- **FP&A Analyst:** As an FP&A Analyst, I want to compare monthly trends and variance percentages, so I can spot when performance starts to diverge from plan.
- **Department Manager:** As a Department Manager, I want a ranked department variance view with account-level drill-down, so I can investigate the cost or revenue lines that need attention.
- **Regional Leader:** As a Regional Leader, I want consistent region filters and the same KPI definitions, so I can compare performance fairly across regions.
- **Data/BI Owner:** As a BI Owner, I want row-grain, foreign-key and reconciliation checks, so decision-makers can trust the dashboard figures.

### Acceptance criteria (sample)
- Actual, budget and variance use a documented definition and matching filters.
- Revenue variance = actual revenue − budget revenue.
- Expense variance = actual expense − budget expense; positive values mean overspend.
- Operating-profit variance = actual operating profit − budget operating profit.
- Month, region, department and account filters affect the visuals consistently in the eventual Birst dashboard.
- Every insight distinguishes an observed pattern from a hypothesis; proposed actions have an owner and follow-up date.
- Synthetic data is clearly disclosed; no claim is made that Birst deployment has been completed.

## Dataset and model
- **1,680 fact rows** = 12 months × 4 regions × 5 departments × 7 accounts.
- Fact grain: one row per month × region × department × account.
- Dimensions: account (with account type), department and region.
- Amounts are synthetic currency examples in USD; do not use them as real company results.

## Tech stack
- **Infor Birst (planned implementation):** model/subject area, measures and attributes, Visualizer reports, dashboard filters, KPI tiles, dashboard publishing and validation.
- **SQL:** finance KPI aggregation, variance breakdowns and quality/reconciliation checks.
- **Python:** pandas/NumPy calculations, data-quality assertions, CSV outputs and Matplotlib charts.
- **GitHub Pages:** responsive, self-contained static portfolio dashboard with KPI figures and four inline SVG charts embedded in `index.html`; the page does not fetch chart images or CSV files at runtime. It is a presentation layer, not a live Birst connection.

## Run locally
Python 3.10+ recommended.

```bash
python -m pip install -r requirements.txt
python python/analyze_finance.py
python python/build_dashboard.py
python -m unittest discover -s tests -v
```

Outputs are written to `outputs/`, including KPI CSVs, department/region/account summaries, findings and charts.

## Project structure
```text
index.html                         # self-contained responsive DDD dashboard; inline KPI values and four SVG charts
README.md                          # project overview and truthful disclosure
data/synthetic/                    # fact and dimension CSVs
sql/                               # schema, KPI queries, QA checks
python/analyze_finance.py          # reproducible analysis and chart generation
python/build_dashboard.py          # embed data-derived KPIs and SVG charts in index.html
.github/workflows/ci.yml           # automated checks on push and pull request
outputs/                           # generated results and four charts
birst/                             # implementation blueprint and report catalogue
docs/                              # user stories, definitions, decision log, QA plan and screenshots
tests/                             # automated validation tests
```

## Infor Birst implementation blueprint
See [`birst/BIRST_FINANCE_MODEL_AND_DASHBOARD_GUIDE.md`](birst/BIRST_FINANCE_MODEL_AND_DASHBOARD_GUIDE.md). It separates the design from a real deployment. In Birst, configure a finance subject area with clear measures and attributes; create KPI tiles and Visualizer reports; add shared date/region/department/account filters; publish a dashboard; and reconcile sampled values against SQL/Python outputs. Only mark implementation complete after doing this inside an authorized Birst practice space.

## Portfolio/resume wording (only claim what you can explain)
**Finance KPI & Budget vs Actual Analytics | SQL, Python, Infor Birst design**
- Built a synthetic finance fact/dimension model and analyzed budget vs actual revenue, COGS, operating expenses, operating profit and margin.
- Created repeatable Python analysis and SQL queries with row-grain, dimension-key and financial reconciliation checks.
- Designed a DDD-oriented dashboard blueprint and user stories for an Infor Birst implementation, with clear variance definitions and decision-focused follow-up.

**Do not say “deployed an Infor Birst dashboard” until you have personally built and validated it in Birst.**

## References
- Infor, [Analytics with Birst](https://developer.infor.com/tutorials/analytics-with-birst): modeling, semantic layer, Visualizer, Designer and dashboards.
- Infor documentation, [Manage subject areas](https://docs.infor.com/birst/2026.x/en-us/birstolh/admin/adminsubjectarea.html): subject areas control which measures/attributes are available to report authors.
- Infor documentation, [Using Smart Insights](https://docs.infor.com/birst/2026.10/en-us/birstolh/dashboards_user/ill1655271262734.html): KPI analysis can use varied attributes, time intervals and dashboard filters; results depend on data volume and configuration.
- Infor, [Dashboard filters and dynamic dimensions/measures](https://developer.infor.com/tutorials/analytics/dynamically-change-measures-and-dimensions-in-a-report-using-a-dashboard-filter/): interactive exploration.
- Data storytelling, [Databricks overview](https://www.databricks.com/blog/what-is-data-storytelling): distinguish dashboards for monitoring from narratives that explain implications and actions.
