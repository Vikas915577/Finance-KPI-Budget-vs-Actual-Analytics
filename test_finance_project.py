from pathlib import Path
import unittest
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "synthetic"

class FinanceProjectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fact = pd.read_csv(DATA / "fact_finance_monthly.csv", parse_dates=["month_start"])
        cls.account = pd.read_csv(DATA / "dim_account.csv")
        cls.region = pd.read_csv(DATA / "dim_region.csv")
        cls.department = pd.read_csv(DATA / "dim_department.csv")

    def test_fact_grain_unique(self):
        self.assertFalse(self.fact.duplicated(["month_start", "region_id", "department_id", "account_id"]).any())

    def test_foreign_keys_resolve(self):
        self.assertTrue(set(self.fact.account_id).issubset(set(self.account.account_id)))
        self.assertTrue(set(self.fact.region_id).issubset(set(self.region.region_id)))
        self.assertTrue(set(self.fact.department_id).issubset(set(self.department.department_id)))

    def test_amounts_nonnegative(self):
        self.assertTrue((self.fact[["budget_amount", "actual_amount"]] >= 0).all().all())

    def test_expected_row_count(self):
        self.assertEqual(len(self.fact), 12 * len(self.region) * len(self.department) * len(self.account))
        self.assertEqual(self.fact.month_start.nunique(), 12)

    def test_account_types_complete(self):
        self.assertEqual(set(self.account.account_type), {"Revenue", "COGS", "Operating Expense"})

if __name__ == "__main__":
    unittest.main()
