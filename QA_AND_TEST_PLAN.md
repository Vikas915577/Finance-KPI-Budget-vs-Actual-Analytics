# QA and Test Plan

## Data checks
- Verify 1,680 rows at month × region × department × account grain.
- Verify the 12 month periods, 4 regions, 5 departments and 7 accounts.
- Check duplicate composite keys, missing keys, invalid amounts and unresolved dimension keys.
- Verify KPI math: operating profit = revenue − COGS − operating expenses.
- Verify variance math: actual − budget using the correct account classification.

## Dashboard checks in Infor Birst (manual, requires authorized Birst access)
- Create/import the model and subject area.
- Validate a sample month and one region against the Python/SQL output.
- Test period, region, department and account filters on every relevant visual.
- Drill from KPI to trend, department, region and account.
- Confirm titles, units, filter state, period, and synthetic-data disclosure.
- Check phone/tablet readability and user permissions.
- Publish only after reconciliation and stakeholder review.

## Limitations
Automated tests cover the local synthetic dataset and calculations. They do not prove a live Birst dashboard exists or that a Birst space has been deployed.
