from pathlib import Path
import unittest
import pandas as pd
from python.analyze_finance import load_data, validate, enrich, pnl_by_period

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"/"synthetic"

class FinanceAnalyticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fact,cls.account,cls.region,cls.dept=load_data(DATA)
    def test_expected_grain_and_row_count(self):
        self.assertEqual(len(self.fact),12*4*5*7)
        self.assertFalse(self.fact.duplicated(["month_start","region_id","department_id","account_id"]).any())
    def test_dimension_keys_resolve(self):
        self.assertTrue(set(self.fact.account_id).issubset(set(self.account.account_id)))
        self.assertTrue(set(self.fact.region_id).issubset(set(self.region.region_id)))
        self.assertTrue(set(self.fact.department_id).issubset(set(self.dept.department_id)))
    def test_amounts_nonnegative_and_present(self):
        self.assertFalse(self.fact[["actual_amount","budget_amount"]].isna().any().any())
        self.assertTrue((self.fact[["actual_amount","budget_amount"]]>=0).all().all())
    def test_validate_passes(self):
        self.assertTrue(validate(self.fact,self.account,self.region,self.dept))
    def test_profit_and_variance_reconcile(self):
        df=enrich(self.fact,self.account,self.region,self.dept)
        monthly=pnl_by_period(df,["month_start"])
        self.assertEqual(len(monthly),12)
        self.assertTrue((abs(monthly.operating_profit_variance-(monthly.operating_profit_actual-monthly.operating_profit_budget))<0.01).all())
    def test_month_coverage(self):
        self.assertEqual(self.fact.month_start.nunique(),12)
    def test_account_classification(self):
        self.assertEqual(set(self.account.account_type),{"Revenue","COGS","Operating Expense"})


class DashboardStaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "index.html").read_text(encoding="utf-8")

    def test_four_charts_are_embedded(self):
        self.assertEqual(self.html.count("<svg"), 4)

    def test_dashboard_does_not_fetch_missing_assets(self):
        self.assertNotIn("fetch(", self.html)
        self.assertNotIn("outputs/charts/", self.html)
        self.assertNotIn("Loading data…", self.html)

    def test_executive_kpis_are_present_without_runtime_csv(self):
        for value in ("$38.97M", "$9.84M", "25.24%", "1,680"):
            self.assertIn(value, self.html)


if __name__=="__main__": unittest.main()
