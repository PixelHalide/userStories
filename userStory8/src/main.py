import logging
from pathlib import Path

from userStory8.src.loader import load_csv
from userStory8.src.reporter import generate_billing_output, generate_summary, write_outputs
from userStory8.src.usage_aggregator import aggregate_usage


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = PROJECT_ROOT / "logs" / "billing.log"


def setup_logging():
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        filemode="w",
    )


def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting billing engine")

    subscriptions = load_csv(PROJECT_ROOT / "data" / "subscriptions.csv")
    usage = load_csv(PROJECT_ROOT / "data" / "usage.csv")

    aggregated_usage = aggregate_usage(usage, month="2024-03")
    billing_output = generate_billing_output(subscriptions, aggregated_usage)
    summary = generate_summary(billing_output)

    write_outputs(
        billing_output,
        summary,
        PROJECT_ROOT / "billing_output.csv",
        PROJECT_ROOT / "billing_summary.json",
    )
    logger.info("Billing engine completed")


if __name__ == "__main__":
    main()
