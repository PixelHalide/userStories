"""Pandas merchant settlement aggregation."""

from __future__ import annotations

import pandas as pd


def calculate_settlements(transactions: pd.DataFrame, merchants: pd.DataFrame) -> pd.DataFrame:
    """Calculate transaction counts and valid settlement totals per merchant."""
    report = merchants[["merchant_id", "merchant_name"]].drop_duplicates("merchant_id")

    all_counts = transactions.groupby("merchant_id").size()
    valid = transactions[transactions["transaction_status"] == "VALID"]
    valid_counts = valid.groupby("merchant_id").size()
    valid_amounts = valid.groupby("merchant_id")["transaction_amount"].sum()

    report = report.copy()
    report["total_transactions"] = report["merchant_id"].map(all_counts).fillna(0).astype(int)
    report["valid_transactions"] = report["merchant_id"].map(valid_counts).fillna(0).astype(int)
    report["fraud_transactions"] = (
        report["total_transactions"] - report["valid_transactions"]
    )
    report["settlement_amount"] = report["merchant_id"].map(valid_amounts).fillna(0.0)
    return report
