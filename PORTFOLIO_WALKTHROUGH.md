# Interview Walkthrough

## 60-second explanation
I built a finance budget-vs-actual analytics portfolio using synthetic monthly data. The fact table has a clear month-region-department-account grain and is joined to account, department and region dimensions. Python creates reproducible finance KPIs and charts, while SQL includes KPI aggregation and data-quality checks. The dashboard design follows Display → Diagnose → Decide: first surface performance against plan, then break down the variance by department/region/account, and finally define an owner-led investigation. I designed an Infor Birst implementation blueprint but would only claim a live Birst deployment after building and reconciling it in a Birst space.

## Questions to be ready for
- Why is the fact grain explicit?
- Why can a positive expense variance be bad while a positive revenue variance is good?
- How is operating profit derived?
- What tests prove dimensions join without duplicating amounts?
- Why does a variance indicate where to investigate but not prove root cause?
- How would you reconcile a Birst KPI to SQL and Python?
- What user decision changes because of this dashboard?
