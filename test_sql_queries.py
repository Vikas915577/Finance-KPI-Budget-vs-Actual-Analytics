"""Exercise the PostgreSQL-compatible SQL logic with an in-memory SQLite fixture.

This validates SELECT semantics and reconciliations without requiring a server.
The project schema/queries target PostgreSQL; SQLite here is a lightweight smoke test.
"""
from pathlib import Path
import csv
import sqlite3
import unittest
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "synthetic"
OUTPUTS = ROOT / "outputs"


def read_csv_rows(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class SqlQuerySmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = sqlite3.connect(":memory:")
        cls.db.execute("PRAGMA foreign_keys = ON")
        cls.db.executescript((ROOT / "sql" / "01_schema_postgresql.sql").read_text(encoding="utf-8"))
        for table, path, columns in [
            ("dim_account", DATA / "dim_account.csv", ["account_id", "account_name", "account_type"]),
            ("dim_department", DATA / "dim_department.csv", ["department_id", "department_name"]),
            ("dim_region", DATA / "dim_region.csv", ["region_id", "region_name"]),
            ("fact_finance_monthly", DATA / "fact_finance_monthly.csv", ["month_start", "region_id", "department_id", "account_id", "budget_amount", "actual_amount"]),
        ]:
            rows = read_csv_rows(path)
            placeholders = ",".join("?" for _ in columns)
            cls.db.executemany(
                f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})",
                [[row[col] for col in columns] for row in rows],
            )
        cls.db.commit()
        cls.sql_text = (ROOT / "sql" / "02_finance_kpi_queries.sql").read_text(encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def section_query(self, section_start, section_end):
        start = self.sql_text.index(section_start)
        end = self.sql_text.find(section_end, start + len(section_start)) if section_end else -1
        section = self.sql_text[start:end] if end >= 0 else self.sql_text[start:]
        query_start = section.upper().find("SELECT")
        if query_start < 0:
            raise AssertionError(f"No SELECT found in SQL section: {section_start}")
        query_end = section.find(";", query_start)
        if query_end < 0:
            raise AssertionError(f"No statement terminator found in SQL section: {section_start}")
        return section[query_start:query_end + 1]

    def test_monthly_revenue_sql_matches_python_output(self):
        query = self.section_query("-- 1) Monthly revenue", "-- 2) Operating profit")
        rows = self.db.execute(query).fetchall()
        expected = pd.read_csv(OUTPUTS / "monthly_pnl_summary.csv").sort_values("month_start")
        self.assertEqual(len(rows), 12)
        for actual, (_, target) in zip(rows, expected.iterrows()):
            self.assertEqual(actual[0], target.month_start)
            self.assertAlmostEqual(actual[1], target.revenue_actual, places=2)
            self.assertAlmostEqual(actual[2], target.revenue_budget, places=2)
            self.assertAlmostEqual(actual[3], target.revenue_variance, places=2)

    def test_department_profit_variance_sql_matches_python_output(self):
        query = self.section_query("-- 2) Operating profit variance", "-- 3) Expense account overspend")
        rows = self.db.execute(query).fetchall()
        expected = pd.read_csv(OUTPUTS / "department_profit_variance.csv").set_index("department_name")
        self.assertEqual(len(rows), 5)
        for name, actual_profit, budget_profit, variance in rows:
            self.assertAlmostEqual(actual_profit, expected.loc[name, "operating_profit_actual"], places=2)
            self.assertAlmostEqual(budget_profit, expected.loc[name, "operating_profit_budget"], places=2)
            self.assertAlmostEqual(variance, expected.loc[name, "operating_profit_variance"], places=2)

    def test_expense_query_uses_actual_minus_budget(self):
        query = self.section_query("-- 3) Expense account overspend", "-- 4) Data-quality")
        rows = self.db.execute(query).fetchall()
        expected = pd.read_csv(OUTPUTS / "account_variance_summary.csv")
        expected = expected[expected.account_type.isin(["COGS", "Operating Expense"])].set_index("account_name")
        self.assertEqual(len(rows), 5)
        for name, actual, budget, variance in rows:
            self.assertAlmostEqual(actual, expected.loc[name, "actual_amount"], places=2)
            self.assertAlmostEqual(budget, expected.loc[name, "budget_amount"], places=2)
            self.assertAlmostEqual(variance, expected.loc[name, "variance_amount"], places=2)

    def test_fact_grain_and_foreign_keys_have_no_violations(self):
        duplicate_query = self.section_query("-- 4) Data-quality", "-- 5) Reconciliation")
        self.assertEqual(self.db.execute(duplicate_query).fetchall(), [])
        for column, dim in [("account_id", "dim_account"), ("department_id", "dim_department"), ("region_id", "dim_region")]:
            result = self.db.execute(
                f"SELECT f.{column} FROM fact_finance_monthly f LEFT JOIN {dim} d USING({column}) WHERE d.{column} IS NULL"
            ).fetchall()
            self.assertEqual(result, [], msg=f"Invalid foreign key for {column}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
