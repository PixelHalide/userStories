"""Run the customer analytics pipeline end-to-end."""
import logging
from pathlib import Path
from .loader import load_customers, load_orders
from .loyalty_engine import add_customer_classifications
from .order_processor import aggregate_customer_orders
from .reporter import write_reports

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def configure_logging(log_path: Path) -> logging.Logger:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=log_path, level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s", force=True)
    return logging.getLogger("customer_analytics")

def run_pipeline(project_root: Path = PROJECT_ROOT) -> dict[str, int | float]:
    logger = configure_logging(project_root / "logs" / "analytics.log")
    logger.info("Customer analytics pipeline started")
    customers = load_customers(project_root / "data" / "customers.csv")
    orders = load_orders(project_root / "data" / "orders.csv")
    report = add_customer_classifications(aggregate_customer_orders(customers, orders, logger))
    summary = write_reports(report, project_root / "customer_loyalty_report.csv", project_root / "analytics_summary.json")
    logger.info("Pipeline completed for %s customers", summary["total_customers"])
    return summary

if __name__ == "__main__":
    print(run_pipeline())
