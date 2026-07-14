"""CSV and JSON analytics output."""
import json
from pathlib import Path
import pandas as pd

REPORT_COLUMNS = ["customer_id", "customer_name", "total_orders", "total_spent", "average_order_value", "loyalty_segment", "customer_activity_status"]

def build_summary(report: pd.DataFrame) -> dict[str, int | float]:
    activity, loyalty = report["customer_activity_status"], report["loyalty_segment"]
    return {
        "total_customers": int(len(report)),
        "active_customers": int(activity.eq("ACTIVE_CUSTOMER").sum()),
        "inactive_customers": int(activity.eq("INACTIVE_CUSTOMER").sum()),
        "platinum_customers": int(loyalty.eq("PLATINUM").sum()),
        "gold_customers": int(loyalty.eq("GOLD").sum()),
        "silver_customers": int(loyalty.eq("SILVER").sum()),
        "bronze_customers": int(loyalty.eq("BRONZE").sum()),
        "total_revenue": round(float(report["total_spent"].sum()), 2),
    }

def write_reports(report: pd.DataFrame, csv_path: str | Path, json_path: str | Path) -> dict[str, int | float]:
    csv_path, json_path = Path(csv_path), Path(json_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    report.loc[:, REPORT_COLUMNS].to_csv(csv_path, index=False)
    summary = build_summary(report)
    json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary
