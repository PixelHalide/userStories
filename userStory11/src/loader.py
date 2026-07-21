"""CSV input loading helpers powered by pandas."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

MERCHANT_COLUMNS = ["merchant_id", "merchant_name", "merchant_category", "country", "status"]
TRANSACTION_COLUMNS = [
    "transaction_id",
    "merchant_id",
    "customer_id",
    "transaction_amount",
    "transaction_time",
    "payment_method",
    "country",
]


def _load_csv(path: str | Path, required_columns: list[str]) -> pd.DataFrame:
    """Load text-oriented CSV data and validate its schema."""
    frame = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    missing = set(required_columns) - set(frame.columns)
    if missing:
        raise ValueError(f"{path} is missing required columns: {', '.join(sorted(missing))}")
    frame = frame.copy()
    frame[required_columns] = frame[required_columns].apply(lambda column: column.str.strip())
    return frame


def load_merchants(path: str | Path) -> pd.DataFrame:
    """Load merchant reference data into a DataFrame."""
    return _load_csv(path, MERCHANT_COLUMNS)


def load_transactions(path: str | Path) -> pd.DataFrame:
    """Load transaction data into a DataFrame in source order."""
    return _load_csv(path, TRANSACTION_COLUMNS)

