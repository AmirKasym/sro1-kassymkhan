"""Kok-Tobe Lift: тесты бизнес-правил для данных."""
import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
with open(ROOT / "data" / "records.csv", encoding="utf-8-sig", newline="") as f:
    ROWS = list(csv.DictReader(f))

COLUMNS = ["ticket_id", "date", "hour", "direction", "passengers", "amount"]
PRICE = {"up": 2000, "down": 2000, "round": 3500}
HOUR_LIMIT = 40


class DataRulesTest(unittest.TestCase):
    def test_columns(self):
        self.assertEqual(list(ROWS[0].keys()), COLUMNS)

    def test_own_records_added(self):
        self.assertGreaterEqual(len(ROWS), 35, "добавьте свои 5 записей в конец records.csv")

    def test_report_created(self):
        report = json.loads((ROOT / "out" / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["records"], len(ROWS))
        self.assertEqual(len(report["control_code"]), 8)

    def test_amount_by_price(self):
        for line, r in enumerate(ROWS, start=2):
            with self.subTest(line=line):
                self.assertIn(r["direction"], PRICE)
                self.assertEqual(int(r["amount"]), int(r["passengers"]) * PRICE[r["direction"]])

    def test_working_hours(self):
        for line, r in enumerate(ROWS, start=2):
            with self.subTest(line=line):
                self.assertTrue(10 <= int(r["hour"]) <= 22)

    def test_hour_limit(self):
        load = {}
        for r in ROWS:
            key = (r["date"], r["hour"])
            load[key] = load.get(key, 0) + int(r["passengers"])
        for key, n in load.items():
            with self.subTest(slot=key):
                self.assertLessEqual(n, HOUR_LIMIT)


if __name__ == "__main__":
    unittest.main()
