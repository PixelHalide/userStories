import json
import tempfile
import unittest
from pathlib import Path
import pandas as pd
from src.loader import load_customers
from src.reporter import REPORT_COLUMNS, build_summary, write_reports

class TestLoaderReporter(unittest.TestCase):
    def test_missing_column_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.csv"
            path.write_text("customer_id,customer_name\nC1,One\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_customers(path)

    def test_summary_and_files(self):
        report = pd.DataFrame([
            dict(zip(REPORT_COLUMNS, ["C1", "One", 1, 10000.0, 10000.0, "PLATINUM", "ACTIVE_CUSTOMER"])),
            dict(zip(REPORT_COLUMNS, ["C2", "Two", 0, 0.0, 0.0, "BRONZE", "INACTIVE_CUSTOMER"])),
        ])
        summary = build_summary(report)
        self.assertEqual(summary["total_revenue"], 10000.0)
        self.assertEqual(summary["gold_customers"], 0)
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "nested" / "report.csv"
            json_path = Path(directory) / "nested" / "summary.json"
            written = write_reports(report, csv_path, json_path)
            self.assertEqual(list(pd.read_csv(csv_path).columns), REPORT_COLUMNS)
            self.assertEqual(json.loads(json_path.read_text()), written)

if __name__ == "__main__":
    unittest.main()
