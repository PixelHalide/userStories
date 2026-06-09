import logging
from pathlib import Path
from typing import TypedDict
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag


BASE_URL = "http://books.toscrape.com/"
OUTPUT_DIR = Path("userStory3/output")
OUTPUT_FILE = "books_data.csv"
REQUIRED_FIELDS = ["Title", "Price", "Rating", "Availability", "URL"]
RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}

logger = logging.getLogger(__name__)


class BookRecord(TypedDict):
    Title: str
    Price: str
    Rating: int
    Availability: str
    URL: str


def get_attribute(tag: Tag, name: str) -> str:
    value = tag.get(name, "")
    return value if isinstance(value, str) else ""


def fetch_page(url: str, attempts: int = 3) -> str | None:
    for _ in range(attempts):
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            response.encoding = response.apparent_encoding or "utf-8"
            return response.text
        except requests.RequestException:
            logger.warning("Could not fetch %s", url, exc_info=True)

    logger.error("Failed to fetch page after %s attempts: %s", attempts, url)
    return None


def parse_books(html: str, page_url: str) -> list[BookRecord]:
    soup = BeautifulSoup(html, "html.parser")
    records: list[BookRecord] = []

    for book in soup.select("article.product_pod"):
        title = book.select_one("h3 a")
        price = book.select_one(".price_color")
        availability = book.select_one(".availability")
        rating = book.select_one(".star-rating")

        if not title or not price or not availability:
            logger.error("Skipping book with missing fields on %s", page_url)
            continue

        rating_classes: list[str] = []
        if rating:
            class_value = rating.get("class")
            if isinstance(class_value, str):
                rating_classes = [class_value]
            elif isinstance(class_value, list):
                rating_classes = [name for name in class_value if isinstance(name, str)]

        rating_name = next((name for name in rating_classes if name in RATING_MAP), "")
        records.append({
            "Title": get_attribute(title, "title") or title.get_text(strip=True),
            "Price": price.get_text(strip=True),
            "Rating": RATING_MAP.get(rating_name, 0),
            "Availability": availability.get_text(" ", strip=True),
            "URL": urljoin(page_url, get_attribute(title, "href")),
        })

    return records


def find_next_page(html: str, page_url: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    next_link = soup.select_one("li.next a")
    if not next_link:
        return None
    return urljoin(page_url, get_attribute(next_link, "href"))


def scrape_books(start_url: str = BASE_URL) -> list[BookRecord]:
    books: list[BookRecord] = []
    page_url: str | None = start_url

    while page_url:
        logger.info("Scraping page: %s", page_url)
        html = fetch_page(page_url)
        if html is None:
            break

        books.extend(parse_books(html, page_url))
        page_url = find_next_page(html, page_url)

    return books


def save_books_to_csv(books: list[BookRecord], output_path: Path | str) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = pd.DataFrame(books, columns=REQUIRED_FIELDS)
    data.to_csv(output_path, index=False)
    return output_path


def scrape_to_csv(
    start_url: str = BASE_URL,
    output_dir: Path | str = OUTPUT_DIR,
    output_file: str = OUTPUT_FILE,
) -> Path:
    output_path = Path(output_dir) / output_file
    books = scrape_books(start_url)
    return save_books_to_csv(books, output_path)
