"""Pandas CSV and JSON report generation."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

PROCESSED_COLUMNS = [
    "transaction_id",
    "merchant_id",
    "customer_id",
    "transaction_amount",
    "transaction_time",
    "fraud_flag",
    "fraud_reason",
    "transaction_status",
]
SETTLEMENT_COLUMNS = [
    "merchant_id",
    "merchant_name",
    "total_transactions",
    "valid_transactions",
    "fraud_transactions",
    "settlement_amount",
]


def build_fraud_summary(transactions: pd.DataFrame) -> dict[str, int]:
    """Calculate required metrics with vectorized Series operations."""
    reasons = transactions["fraud_reason"]
    return {
        "total_transactions": int(len(transactions)),
        "valid_transactions": int(transactions["transaction_status"].eq("VALID").sum()),
        "fraud_transactions": int(transactions["transaction_status"].eq("SUSPICIOUS").sum()),
        "high_value_frauds": int(reasons.str.contains(r"(?:^|;)HIGH_VALUE_TRANSACTION(?:;|$)").sum()),
        "cross_border_frauds": int(reasons.str.contains(r"(?:^|;)CROSS_BORDER_TRANSACTION(?:;|$)").sum()),
        "rapid_transaction_frauds": int(reasons.str.contains(r"(?:^|;)RAPID_TRANSACTIONS(?:;|$)").sum()),
    }


def write_reports(
    transactions: pd.DataFrame,
    settlements: pd.DataFrame,
    output_directory: str | Path,
) -> dict[str, int]:
    """Write processed, settlement, and summary reports with pandas."""
    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)

    processed_output = transactions[PROCESSED_COLUMNS].copy()
    processed_output["transaction_time"] = processed_output["transaction_time"].dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    processed_output["fraud_flag"] = processed_output["fraud_flag"].map(
        {True: "TRUE", False: "FALSE"}
    )
    processed_output.to_csv(output_directory / "processed_transactions.csv", index=False)
    settlements[SETTLEMENT_COLUMNS].to_csv(
        output_directory / "merchant_settlement_report.csv", index=False, float_format="%.2f"
    )

    summary = build_fraud_summary(transactions)
    with (output_directory / "fraud_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")
    return summary
