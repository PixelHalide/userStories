import logging
from pathlib import Path

from src.inventory_engine import reconcile_inventory
from src.loader import load_inventory, load_sales_transactions
from src.reporter import build_sales_summary, write_reports
from src.sales_aggregator import aggregate_april_sales


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def configure_logging() -> logging.Logger:
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        filename=log_dir / "inventory.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        force=True,
    )
    return logging.getLogger("inventory")


def run() -> dict:
    logger = configure_logging()
    inventory = load_inventory(PROJECT_ROOT / "data" / "inventory.csv")
    sales = load_sales_transactions(PROJECT_ROOT / "data" / "sales_transactions.csv")

    sales_summary, processed_count = aggregate_april_sales(sales, inventory, logger)
    reconciled = reconcile_inventory(inventory, sales_summary, logger)
    summary = build_sales_summary(reconciled, processed_count)
    write_reports(reconciled, summary, PROJECT_ROOT)

    logger.info("Inventory reconciliation completed")
    return summary


if __name__ == "__main__":
    print(run())
