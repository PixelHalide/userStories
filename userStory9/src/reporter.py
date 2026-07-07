import json
from pathlib import Path

import pandas as pd


def build_sales_summary(reconciled_df: pd.DataFrame, transactions_processed: int) -> dict:
    return {
        "total_products": int(len(reconciled_df)),
        "total_transactions_processed": int(transactions_processed),
        "total_sales_value": float(reconciled_df["total_sales_value"].sum()),
        "low_stock_products": int((reconciled_df["stock_status"] == "LOW_STOCK").sum()),
        "out_of_stock_products": int((reconciled_df["stock_status"] == "OUT_OF_STOCK").sum()),
    }


def write_reports(reconciled_df: pd.DataFrame, summary: dict, output_dir: str | Path) -> None:
    output_path = Path(output_dir)
    reconciled_df.to_csv(output_path / "inventory_reconciliation.csv", index=False)
    with (output_path / "sales_summary.json").open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)
