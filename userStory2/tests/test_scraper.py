import tempfile
import unittest
from pathlib import Path

import pandas as pd

from userStory2.src.scraper.mapper import REQUIRED_FIELDS, map_data
from userStory2.src.scraper.scraper import (
    FILE_URL,
    download_file,
    identify_file_type_from_url,
)


class ScraperTests(unittest.TestCase):
    temp_dir: tempfile.TemporaryDirectory
    output_dir: Path
    file_type: str | None
    file_path: Path | None
    df: pd.DataFrame

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.output_dir = Path(cls.temp_dir.name)
        cls.file_type = identify_file_type_from_url(FILE_URL)
        cls.file_path = download_file(FILE_URL, output_dir=cls.output_dir)
        cls.df = map_data(cls.file_path)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_1_verify_csv_file_download(self):
        self.assertTrue(self.file_path.exists()) # type: ignore
        self.assertGreater(self.file_path.stat().st_size, 0) # type: ignore

    def test_2_verify_csv_file_extraction(self):
        self.assertIsInstance(self.df, pd.DataFrame)
        self.assertGreater(len(self.df), 0)

    def test_3_validate_file_type_and_format(self):
        self.assertTrue(str(self.file_path).endswith(".csv"))
        self.assertEqual(self.file_type, "csv")

    def test_4_validate_data_structure(self):
        self.assertEqual(list(self.df.columns), REQUIRED_FIELDS)
        self.assertTrue(all(field in self.df.columns for field in REQUIRED_FIELDS))

    def test_5_handle_missing_or_invalid_data(self):
        invalid_file = self.output_dir / "invalid.csv"
        invalid_file.write_text("User Id,First Name\n1,Ada\n")

        with self.assertRaisesRegex(ValueError, "Missing required fields"):
            map_data(invalid_file)


if __name__ == "__main__":
    unittest.main()
