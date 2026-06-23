import tempfile
import unittest
from pathlib import Path

import coverage
import pandas as pd

MAPPER_SOURCE = str(Path(__file__).resolve().parents[1] / "src" / "*.py")
coverage_runner = coverage.Coverage(data_file=None)
coverage_runner.start()

from userStory7.src.mapper import map_data, save_mapped_output


class MapperTests(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        coverage_runner.stop()
        print("\nCoverage report:")
        coverage_runner.report(include=[MAPPER_SOURCE], show_missing=True)

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp_dir.name)
        self.raw_path = self.directory / "raw_data.csv"
        self.reference_path = self.directory / "reference_data.xlsx"

        pd.DataFrame({"lookup_key": ["B", "A", "B", "missing"]}).to_csv(
            self.raw_path, index=False
        )
        pd.DataFrame(
            {
                "lookup_key": ["A", "B", "C"],
                "project_name": ["Alpha", "Beta", "Gamma"],
                "status": ["Active", "Pending", "Inactive"],
            }
        ).to_excel(self.reference_path, index=False)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_only_matching_reference_rows_are_returned(self):
        result = map_data(self.raw_path, self.reference_path)

        self.assertEqual(result["lookup_key"].tolist(), ["A", "B"])

    def test_output_contains_all_reference_columns(self):
        result = map_data(self.raw_path, self.reference_path)

        self.assertEqual(
            result.columns.tolist(), ["lookup_key", "project_name", "status"]
        )

    def test_repeated_raw_values_do_not_create_duplicates(self):
        result = map_data(self.raw_path, self.reference_path)

        self.assertFalse(result["lookup_key"].duplicated().any())
        self.assertEqual(len(result), 2)

    def test_mapped_output_csv_is_created(self):
        output_path = self.directory / "output" / "mapped_output.csv"

        saved_path = save_mapped_output(
            self.raw_path, self.reference_path, output_path
        )

        self.assertEqual(saved_path, output_path)
        self.assertTrue(output_path.exists())
        self.assertEqual(len(pd.read_csv(output_path)), 2)

    def test_missing_lookup_column_raises_error(self):
        pd.DataFrame({"wrong_column": ["A"]}).to_csv(self.raw_path, index=False)

        with self.assertRaisesRegex(ValueError, "lookup_key"):
            map_data(self.raw_path, self.reference_path)


if __name__ == "__main__":
    unittest.main()
