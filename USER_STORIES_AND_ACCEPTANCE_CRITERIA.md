# User Stories and Acceptance Criteria

## Story 1 — Finance Director: executive performance
**As a** Finance Director, **I want** to see revenue, operating profit and margin against budget, **so that** I can prioritize the monthly performance review.

Acceptance:
- KPI cards show actual, budget, absolute variance and variance % where meaningful.
- The selected reporting period is always visible.
- Favourable/unfavourable labels follow the metric's business meaning, not just the sign.

## Story 2 — FP&A Analyst: trend monitoring
**As an** FP&A Analyst, **I want** a month-by-month actual vs budget trend, **so that** I can identify when the plan begins to diverge.

Acceptance:
- Actual and budget use the same date grain and filter context.
- Variance definition is available near the chart.
- Missing months are flagged rather than silently interpreted as zero.

## Story 3 — Department Manager: diagnose drivers
**As a** Department Manager, **I want** departments ranked by operating-profit variance and the underlying account variances, **so that** I can find the most material investigation areas.

Acceptance:
- Variances are sorted by magnitude or business priority.
- The account and department definitions are consistent.
- The chart identifies variance as a signal to investigate, not proof of root cause.

## Story 4 — Regional Leader: compare fairly
**As a** Regional Leader, **I want** shared region and period filters, **so that** I can compare regional results using the same definitions.

Acceptance:
- Filter selections apply consistently to all relevant visuals.
- The current filter state is visible.
- Totals reconcile to the filtered source rows.

## Story 5 — BI/Data Owner: trusted numbers
**As a** BI/Data Owner, **I want** automated data quality and reconciliation checks, **so that** stakeholders can trust the metrics.

Acceptance:
- Fact grain is unique.
- Foreign keys resolve to dimensions.
- Actual and budget amounts are present and valid under the dataset assumptions.
- Aggregated operating profit equals revenue minus COGS minus operating expense.
- Generated outputs are reproducible from the checked-in synthetic data.

## Decision record
The dashboard follows **Display → Diagnose → Decide**:
1. Display the headline result against a plan.
2. Diagnose the largest contributing slice using dimensions and drill-down.
3. Decide on an investigation/action with an owner, due date and next-period check.

A correlation or variance alone does not establish causation. Validate price, volume, mix, timing, allocation and coding before stating a root cause.
