from pathlib import Path
from html import escape
import unittest
import pandas as pd
from bs4 import BeautifulSoup

from python.analyze_finance import load_data, validate, enrich, pnl_by_period
from python.build_dashboard import build, money_k_signed, signed_pct

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "synthetic"
OUTPUTS = ROOT / "outputs"


class FinanceAnalyticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fact, cls.account, cls.region, cls.dept = load_data(DATA)

    def test_expected_grain_and_row_count(self):
        self.assertEqual(len(self.fact), 12 * 4 * 5 * 7)
        self.assertFalse(self.fact.duplicated(["month_start", "region_id", "department_id", "account_id"]).any())

    def test_dimension_keys_resolve(self):
        self.assertTrue(set(self.fact.account_id).issubset(set(self.account.account_id)))
        self.assertTrue(set(self.fact.region_id).issubset(set(self.region.region_id)))
        self.assertTrue(set(self.fact.department_id).issubset(set(self.dept.department_id)))

    def test_amounts_nonnegative_and_present(self):
        self.assertFalse(self.fact[["actual_amount", "budget_amount"]].isna().any().any())
        self.assertTrue((self.fact[["actual_amount", "budget_amount"]] >= 0).all().all())

    def test_validate_passes(self):
        self.assertTrue(validate(self.fact, self.account, self.region, self.dept))

    def test_profit_and_variance_reconcile(self):
        df = enrich(self.fact, self.account, self.region, self.dept)
        monthly = pnl_by_period(df, ["month_start"])
        self.assertEqual(len(monthly), 12)
        self.assertTrue((abs(monthly.operating_profit_variance - (monthly.operating_profit_actual - monthly.operating_profit_budget)) < 0.01).all())

    def test_month_coverage(self):
        self.assertEqual(self.fact.month_start.nunique(), 12)
        self.assertEqual(self.fact.month_start.min().strftime("%Y-%m-%d"), "2025-01-01")
        self.assertEqual(self.fact.month_start.max().strftime("%Y-%m-%d"), "2025-12-01")

    def test_account_classification(self):
        self.assertEqual(set(self.account.account_type), {"Revenue", "COGS", "Operating Expense"})

    def test_budget_and_actual_totals_reconcile_to_fact(self):
        kpis = pd.read_csv(OUTPUTS / "executive_kpis.csv").set_index("metric")["value"]
        self.assertAlmostEqual(kpis.revenue_actual, self.fact.merge(self.account, on="account_id").query("account_type == 'Revenue'").actual_amount.sum(), places=2)
        self.assertAlmostEqual(kpis.revenue_budget, self.fact.merge(self.account, on="account_id").query("account_type == 'Revenue'").budget_amount.sum(), places=2)

    def test_duplicate_fact_grain_is_rejected(self):
        invalid = pd.concat([self.fact, self.fact.iloc[[0]]], ignore_index=True)
        with self.assertRaisesRegex(ValueError, "Duplicate fact grain"):
            validate(invalid, self.account, self.region, self.dept)

    def test_orphan_dimension_key_is_rejected(self):
        invalid = self.fact.copy()
        invalid.loc[invalid.index[0], "account_id"] = "MISSING_ACCOUNT"
        with self.assertRaisesRegex(ValueError, "Unmatched account_id"):
            validate(invalid, self.account, self.region, self.dept)

    def test_negative_amount_is_rejected(self):
        invalid = self.fact.copy()
        invalid.loc[invalid.index[0], "actual_amount"] = -1
        with self.assertRaisesRegex(ValueError, "Negative line-item amounts"):
            validate(invalid, self.account, self.region, self.dept)

    def test_missing_financial_amount_is_rejected(self):
        invalid = self.fact.copy()
        invalid.loc[invalid.index[0], "actual_amount"] = float("nan")
        with self.assertRaisesRegex(ValueError, "Missing financial amounts"):
            validate(invalid, self.account, self.region, self.dept)

    def test_dimension_primary_keys_are_unique(self):
        for dimension, key in [(self.account, "account_id"), (self.region, "region_id"), (self.dept, "department_id")]:
            self.assertFalse(dimension[key].duplicated().any(), msg=f"Duplicate dimension key: {key}")

    def test_operating_profit_formula_reconciles(self):
        df = enrich(self.fact, self.account, self.region, self.dept)
        monthly = pnl_by_period(df, ["month_start"])
        self.assertTrue((abs(monthly.operating_profit_actual - (monthly.revenue_actual - monthly.cogs_actual - monthly.opex_actual)) < 0.01).all())
        self.assertTrue((abs(monthly.operating_profit_budget - (monthly.revenue_budget - monthly.cogs_budget - monthly.opex_budget)) < 0.01).all())


class DashboardStaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = ROOT / "index.html"
        cls.html = cls.path.read_text(encoding="utf-8")
        cls.soup = BeautifulSoup(cls.html, "html.parser")

    def test_four_accessible_charts_are_embedded(self):
        charts = self.soup.find_all("svg")
        self.assertEqual(len(charts), 4)
        self.assertTrue(all(c.get("role") == "img" and c.get("aria-label") for c in charts))

    def test_dashboard_has_no_runtime_data_or_chart_dependencies(self):
        self.assertNotIn("fetch(", self.html)
        self.assertNotIn("outputs/charts/", self.html)
        self.assertNotIn("Loading data", self.html)
        self.assertEqual(len(self.soup.find_all("img")), 0)
        self.assertEqual([a.get("href") for a in self.soup.find_all(href=True) if a["href"].startswith(".")], [])

    def test_executive_kpis_match_generated_csv(self):
        k = pd.read_csv(OUTPUTS / "executive_kpis.csv").set_index("metric")["value"]
        expected = {
            "kpi-revenue-actual": f"${k.revenue_actual/1_000_000:.2f}M",
            "kpi-revenue-budget": f"${k.revenue_budget/1_000_000:.2f}M",
            "kpi-profit-actual": f"${k.operating_profit_actual/1_000_000:.2f}M",
            "kpi-profit-budget": f"${k.operating_profit_budget/1_000_000:.2f}M",
            "kpi-margin-actual": f"{k.operating_margin_actual_pct:.2f}%",
            "kpi-margin-budget": f"{k.operating_margin_budget_pct:.2f}%",
        }
        for element_id, value in expected.items():
            with self.subTest(kpi=element_id):
                self.assertEqual(self.soup.find(id=element_id).get_text(strip=True), value)
        revenue_variance = float(k.revenue_variance)
        expected_revenue_variance = f"{money_k_signed(revenue_variance)} · {signed_pct(revenue_variance / float(k.revenue_budget) * 100)} vs budget"
        profit_variance = float(k.operating_profit_variance)
        expected_profit_variance = f"{money_k_signed(profit_variance)} · {signed_pct(profit_variance / float(k.operating_profit_budget) * 100)} vs budget"
        self.assertEqual(self.soup.find(id="kpi-revenue-variance").get_text(strip=True), expected_revenue_variance)
        self.assertEqual(self.soup.find(id="kpi-profit-variance").get_text(strip=True), expected_profit_variance)

    def test_charts_reflect_generated_outputs(self):
        monthly = pd.read_csv(OUTPUTS / "monthly_pnl_summary.csv")
        depts = pd.read_csv(OUTPUTS / "department_profit_variance.csv")
        accounts = pd.read_csv(OUTPUTS / "account_variance_summary.csv")
        first = monthly.iloc[0]
        last = monthly.iloc[-1]
        self.assertIn(f"Jan actual revenue: ${first.revenue_actual:,.0f}", self.html)
        self.assertIn(f"Dec budget revenue: ${last.revenue_budget:,.0f}", self.html)
        worst = depts.loc[depts.operating_profit_variance.idxmin()]
        self.assertIn(f"{worst.department_name}: ${worst.operating_profit_variance:,.2f}", self.html)
        top_expense = accounts[accounts.account_type.eq("Operating Expense")].loc[accounts[accounts.account_type.eq("Operating Expense")].variance_amount.idxmax()]
        self.assertIn(escape(f"{top_expense.account_name}: ${top_expense.variance_amount:,.2f}"), self.html)
        self.assertIn("Monthly actual revenue versus actual operating margin using observed monthly values", self.html)

    def test_dashboard_contains_data_derived_recommendation(self):
        depts = pd.read_csv(OUTPUTS / "department_profit_variance.csv")
        accounts = pd.read_csv(OUTPUTS / "account_variance_summary.csv")
        best = depts.loc[depts.operating_profit_variance.idxmax()]
        worst = depts.loc[depts.operating_profit_variance.idxmin()]
        expenses = accounts[accounts.account_type.eq("Operating Expense")]
        top_expense = expenses.loc[expenses.variance_amount.idxmax()]
        department_text = self.soup.find(id="finding-department-text").get_text(" ", strip=True)
        account_text = self.soup.find(id="finding-account-text").get_text(" ", strip=True)
        self.assertIn(str(best.department_name), department_text)
        self.assertIn(str(worst.department_name), department_text)
        self.assertIn(money_k_signed(float(top_expense.variance_amount)), account_text)
        self.assertIn("do not assume cause", department_text)

    def test_mobile_responsive_rules_are_present(self):
        self.assertIn("@media(max-width:780px)", self.html)
        self.assertIn("@media(max-width:520px)", self.html)
        self.assertIn('name="viewport"', self.html)

    def test_dashboard_build_is_reproducible(self):
        before = self.path.read_bytes()
        build()
        after = self.path.read_bytes()
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main(verbosity=2)
