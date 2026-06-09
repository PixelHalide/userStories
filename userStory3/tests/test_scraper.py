import tempfile
import unittest
from pathlib import Path

import coverage
import pandas as pd

SCRAPER_SOURCE = str(Path(__file__).resolve().parents[1] / "src" / "scraper" / "*.py")
coverage_runner = coverage.Coverage(data_file=None)
coverage_runner.start()

from userStory3.src.scraper.scraper import (
    BASE_URL,
    REQUIRED_FIELDS,
    fetch_page,
    find_next_page,
    parse_books,
    save_books_to_csv,
    scrape_books,
)


class BookScraperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.first_page_html = fetch_page(BASE_URL)
        if cls.first_page_html is None:
            raise RuntimeError("Could not fetch Books to Scrape home page")

        cls.first_page_books = parse_books(cls.first_page_html, BASE_URL)
        cls.all_books = scrape_books(BASE_URL)

    @classmethod
    def tearDownClass(cls):
        coverage_runner.stop()
        print("\nCoverage report:")
        coverage_runner.report(include=[SCRAPER_SOURCE], show_missing=True)

    def test_1_verify_csv_file_creation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = save_books_to_csv(self.all_books, Path(temp_dir) / "books_data.csv")

            self.assertTrue(output_path.exists())
            self.assertGreater(output_path.stat().st_size, 0)

    def test_2_verify_first_page_data_extraction(self):
        self.assertEqual(len(self.first_page_books), 20)
        self.assertEqual(self.first_page_books[0]["Title"], "A Light in the Attic")
        self.assertEqual(self.first_page_books[0]["Price"], "£51.77")
        self.assertEqual(self.first_page_books[0]["Rating"], 3)
        self.assertEqual(self.first_page_books[0]["Availability"], "In stock")
        self.assertTrue(self.first_page_books[0]["URL"].startswith("http://books.toscrape.com/catalogue/"))

    def test_3_validate_file_type_and_format(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = save_books_to_csv(self.all_books, Path(temp_dir) / "books_data.csv")
            data = pd.read_csv(output_path)

            self.assertEqual(output_path.suffix, ".csv")
            self.assertEqual(len(data), 1000)

    def test_4_validate_data_structure(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = save_books_to_csv(self.all_books, Path(temp_dir) / "books_data.csv")
            data = pd.read_csv(output_path)

            self.assertEqual(list(data.columns), REQUIRED_FIELDS)
            self.assertFalse(data[REQUIRED_FIELDS].isna().any().any())

    def test_5_handle_invalid_page_without_failure(self):
        with self.assertLogs("userStory3.src.scraper.scraper", level="ERROR"):
            html = fetch_page("http://books.toscrape.com/does-not-exist.html", attempts=1)

        self.assertIsNone(html)

    def test_scrapes_all_paginated_books(self):
        self.assertEqual(len(self.all_books), 1000)
        self.assertEqual(min(book["Rating"] for book in self.all_books), 1)
        self.assertEqual(max(book["Rating"] for book in self.all_books), 5)

    def test_finds_next_page_on_real_site(self):
        assert self.first_page_html is not None
        self.assertEqual(
            find_next_page(self.first_page_html, BASE_URL),
            "http://books.toscrape.com/catalogue/page-2.html",
        )


if __name__ == "__main__":
    unittest.main()
