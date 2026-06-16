from __future__ import annotations

import csv
import json
import os
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_CSV = BASE_DIR.parent / "userStory3" / "output" / "books_data.csv"
OUTPUT_CSV = BASE_DIR / "output" / "books_data_clean_powerbi.csv"

load_dotenv(BASE_DIR / ".env")


class BooksDataConversionError(RuntimeError):
    pass


def fetch_gbp_to_usd_rate(
    currency_url: str | None = None,
    timeout: float = 10.0,
) -> Decimal:
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise BooksDataConversionError(
            "API_KEY is not set. Add the currency conversion API key to the environment."
        )

    if currency_url is None:
        currency_url = f"https://api.currencyapi.com/v3/latest?apikey={api_key}"

    request = Request(currency_url, headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        rate = payload["data"]["USD"]["value"]
        return Decimal(str(rate))
    except Exception as exc:
        raise BooksDataConversionError("Failed to fetch USD exchange rate.") from exc


def parse_price(value: Any) -> Decimal:
    price_text = str(value).strip().replace("£", "").replace(",", "")
    if not price_text:
        raise BooksDataConversionError("Encountered an empty price value.")
    try:
        return Decimal(price_text)
    except InvalidOperation as exc:
        raise BooksDataConversionError(f"Invalid price value: {value!r}") from exc


def normalize_title(value: Any) -> str:
    return " ".join(str(value).split())


def normalize_availability(value: Any) -> str:
    text = " ".join(str(value).split()).strip().lower()
    if not text:
        return ""
    if "out" in text:
        return "Out of stock"
    return "In stock"


def normalize_rating(value: Any) -> int:
    try:
        rating = int(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise BooksDataConversionError(f"Invalid rating value: {value!r}") from exc

    if rating < 1 or rating > 5:
        raise BooksDataConversionError(f"Rating out of range: {rating}")
    return rating


def price_category(price_gbp: Decimal) -> str:
    if price_gbp < Decimal("20"):
        return "Budget"
    if price_gbp <= Decimal("50"):
        return "Standard"
    return "Premium"


def quantize_currency(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def load_and_clean_rows(rate: Decimal) -> list[dict[str, str]]:
    seen: set[tuple[str, str]] = set()
    rows: list[dict[str, str]] = []

    with INPUT_CSV.open(newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        for raw_row in reader:
            title = normalize_title(raw_row.get("Title", ""))
            url = str(raw_row.get("URL", "")).strip()
            price_text = raw_row.get("Price", "")
            rating_text = raw_row.get("Rating", "")
            availability_text = raw_row.get("Availability", "")

            if not title or not url or not price_text or not rating_text:
                continue

            dedupe_key = (title.lower(), url)
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            price_gbp = parse_price(price_text)
            price_usd = quantize_currency(price_gbp * rate)
            rating = normalize_rating(rating_text)
            availability = normalize_availability(availability_text)

            if not availability:
                continue

            rows.append(
                {
                    "Title": title,
                    "Price_GBP": f"{quantize_currency(price_gbp):.2f}",
                    "Price_USD": f"{price_usd:.2f}",
                    "Rating": str(rating),
                    "Availability": availability,
                    "Price_Category": price_category(price_gbp),
                    "URL": url,
                }
            )

    return rows


def write_output(rows: list[dict[str, str]]) -> None:
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=[
                "Title",
                "Price_GBP",
                "Price_USD",
                "Rating",
                "Availability",
                "Price_Category",
                "URL",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if not INPUT_CSV.exists():
        raise BooksDataConversionError(f"Input CSV not found: {INPUT_CSV}")

    rate = fetch_gbp_to_usd_rate()
    rows = load_and_clean_rows(rate)
    write_output(rows)
    print(f"Wrote {len(rows)} cleaned book rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
