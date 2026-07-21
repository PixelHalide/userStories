"""Vectorized transaction validation and normalization."""

from __future__ import annotations

import logging

import pandas as pd

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def validate_transactions(
    transactions: pd.DataFrame,
    merchants: pd.DataFrame,
    logger: logging.Logger | None = None,
) -> pd.DataFrame:
    """Return valid transactions; log and exclude invalid rows."""
    logger = logger or logging.getLogger(__name__)
    frame = transactions.copy()
    merchant_lookup = merchants.drop_duplicates("merchant_id", keep="last").set_index("merchant_id")

    frame["transaction_amount"] = pd.to_numeric(frame["transaction_amount"], errors="coerce")
    frame["transaction_time"] = pd.to_datetime(
        frame["transaction_time"], format=TIMESTAMP_FORMAT, errors="coerce"
    )
    frame["merchant_status"] = frame["merchant_id"].map(merchant_lookup["status"])

    def validation_error(transaction: pd.Series) -> str | None:
        if pd.isna(transaction["merchant_status"]):
            return "unknown merchant"
        if transaction["merchant_status"].upper() == "BLOCKED":
            return "blocked merchant"
        amount = transaction["transaction_amount"]
        if pd.isna(amount) or amount in (float("inf"), float("-inf")) or amount <= 0:
            return "transaction amount must be a positive finite number"
        if pd.isna(transaction["transaction_time"]):
            return "invalid transaction timestamp"
        return None

    frame["validation_error"] = frame.apply(validation_error, axis=1)
    rejected = frame[frame["validation_error"].notna()]
    for transaction in rejected.itertuples():
        logger.error(
            "Rejected transaction %s: %s",
            transaction.transaction_id,
            transaction.validation_error,
        )

    valid = frame[frame["validation_error"].isna()]
    return valid.drop(columns=["merchant_status", "validation_error"]).reset_index(drop=True)
