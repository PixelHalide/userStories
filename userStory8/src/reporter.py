import json
import logging
from pathlib import Path

import pandas as pd

from userStory8.src.billing_engine import calculate_bill
from userStory8.src.status_engine import evaluate_status


logger = logging.getLogger(__name__)


OUTPUT_COLUMNS = [
    "subscription_id",
    "customer_id",
    "plan",
    "total_usage_gb",
    "overage_gb",
    "total_bill",
    "final_status",
]


def generate_billing_output(subscriptions_df, aggregated_usage_df):
    """Generate billing rows for all subscriptions, including cancelled rows."""
    data = subscriptions_df.copy()
    data["monthly_fee"] = pd.to_numeric(data["monthly_fee"], errors="coerce").fillna(0)
    data["usage_limit_gb"] = pd.to_numeric(data["usage_limit_gb"], errors="coerce").fillna(0)

    data = data.merge(aggregated_usage_df, on="subscription_id", how="left")
    data["total_usage_gb"] = pd.to_numeric(data["total_usage_gb"], errors="coerce").fillna(0)

    data[["overage_gb", "total_bill"]] = data.apply(
        lambda row: pd.Series(
            calculate_bill(
                row["monthly_fee"],
                row["usage_limit_gb"],
                row["total_usage_gb"],
                row["status"],
            )
        ),
        axis=1,
    )
    data["final_status"] = data.apply(
        lambda row: evaluate_status(row["status"], row["total_usage_gb"], row["usage_limit_gb"]),
        axis=1,
    )

    data["total_usage_gb"] = data["total_usage_gb"].round(2)
    data["overage_gb"] = data["overage_gb"].round(2)
    data["total_bill"] = data["total_bill"].round(2)

    return data[OUTPUT_COLUMNS]


def generate_summary(billing_output_df):
    """Create billing summary metrics from output rows."""
    status_counts = billing_output_df["final_status"].value_counts()
    total_subscriptions = len(billing_output_df)
    total_revenue = billing_output_df["total_bill"].sum()

    return {
        "total_subscriptions": total_subscriptions,
        "active_subscriptions": int(status_counts.get("ACTIVE", 0)),
        "suspended_subscriptions": int(status_counts.get("SUSPENDED", 0)),
        "cancelled_subscriptions": int(status_counts.get("CANCELLED", 0)),
        "total_revenue": round(float(total_revenue), 2),
        "average_bill": round(float(total_revenue / total_subscriptions), 2),
    }


def write_outputs(billing_output_df, summary, output_csv_path, summary_json_path):
    """Write CSV and JSON outputs."""
    output_csv = Path(output_csv_path)
    summary_json = Path(summary_json_path)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    summary_json.parent.mkdir(parents=True, exist_ok=True)

    billing_output_df.to_csv(output_csv, index=False)
    with summary_json.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)

    logger.info("Wrote billing output to %s", output_csv)
    logger.info("Wrote billing summary to %s", summary_json)
