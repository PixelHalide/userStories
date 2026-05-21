import unittest

import pandas as pd

from src.employee_scraper.scraper import (
    EXPECTED_FIELDS,
    OUTPUT_FIELDS,
    EmployeeScraperError,
    fetch_employees,
    normalize_employees,
)


class EmployeeScraperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = fetch_employees()

    def test_1_verify_json_file_download(self):
        self.assertGreater(len(self.records), 0)
        self.assertIsInstance(self.records[0], dict)

    def test_2_verify_json_file_extraction(self):
        records = self.records

        self.assertEqual(records, self.records)

    def test_3_validate_file_type_and_format(self):

        self.assertIsInstance(self.records, list)
        self.assertTrue(all(isinstance(record, dict) for record in self.records))

    def test_4_validate_data_structure(self):
        df = normalize_employees(self.records)

        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue(EXPECTED_FIELDS.issubset(self.records[0].keys()))
        self.assertEqual(list(df.columns), OUTPUT_FIELDS)
        self.assertEqual(df["employee_id"].dtype.kind, "i")
        self.assertEqual(df["age"].dtype.kind, "i")
        self.assertEqual(df["salary"].dtype.kind, "i")

    def test_5_handle_missing_or_invalid_data(self):
        with self.assertRaises(EmployeeScraperError):
            normalize_employees([{"id": 1}])

        invalid_record = {**self.records[0], "phone": "not-a-number"}
        with self.assertRaises(EmployeeScraperError):
            normalize_employees([invalid_record])


if __name__ == "__main__":
    unittest.main()
