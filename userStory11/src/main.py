"""Run the payment fraud and settlement pipeline."""

from __future__ import annotations

import logging
from pathlib import Path

from .fraud_engine import apply_fraud_rules
from .loader import load_merchants, load_transactions
from .reporter import write_reports
from .settlement_engine import calculate_settlements
from .validator import validate_transactions

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def configure_logging(log_path: Path) -> logging.Logger:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        force=True,
    )
    return logging.getLogger("fraud_engine")


def run_pipeline(project_root: str | Path = PROJECT_ROOT) -> dict[str, int]:
    """Execute loading, validation, fraud detection, and reporting."""
    project_root = Path(project_root)
    logger = configure_logging(project_root / "logs" / "fraud_engine.log")
    logger.info("Fraud detection and settlement pipeline started")

    merchants = load_merchants(project_root / "data" / "merchants.csv")
    raw_transactions = load_transactions(project_root / "data" / "transactions.csv")
    validated = validate_transactions(raw_transactions, merchants, logger)
    processed = apply_fraud_rules(validated, merchants)
    settlements = calculate_settlements(processed, merchants)
    summary = write_reports(processed, settlements, project_root / "outputs")

    logger.info(
        "Pipeline completed: %s input, %s processed, %s rejected",
        len(raw_transactions),
        len(processed),
        len(raw_transactions) - len(processed),
    )
    return summary


if __name__ == "__main__":
    print(run_pipeline())
