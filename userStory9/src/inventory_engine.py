import logging

import pandas as pd


def get_stock_status(final_stock: int) -> str:
    if final_stock == 0:
        return "OUT_OF_STOCK"
    if final_stock <= 10:
        return "LOW_STOCK"
    return "AVAILABLE"


def _merge_sales(inventory_df: pd.DataFrame, sales_summary_df: pd.DataFrame) -> pd.DataFrame:
    result = inventory_df.merge(sales_summary_df, on="product_id", how="left")
    result["total_sold_quantity"] = result["total_sold_quantity"].fillna(0).astype(int)
    return result


def _calculate_final_stock(result: pd.DataFrame, logger: logging.Logger) -> pd.Series:
    raw_final_stock = result["current_stock"] - result["total_sold_quantity"]

    for _, row in result[raw_final_stock < 0].iterrows():
        logger.warning("STOCK_ERROR: product_id=%s sold=%s stock=%s", row["product_id"], row["total_sold_quantity"], row["current_stock"])

    return raw_final_stock.clip(lower=0).astype(int)


def _add_inventory_fields(result: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    result = result.copy()
    result["final_stock"] = _calculate_final_stock(result, logger)
    result["stock_status"] = result["final_stock"].apply(get_stock_status)
    result["total_sales_value"] = result["total_sold_quantity"] * result["unit_price"]
    return result


def _select_report_columns(result: pd.DataFrame) -> pd.DataFrame:
    return result[
        [
            "product_id",
            "product_name",
            "category",
            "current_stock",
            "total_sold_quantity",
            "final_stock",
            "stock_status",
            "total_sales_value",
        ]
    ]


def reconcile_inventory(
    inventory_df: pd.DataFrame,
    sales_summary_df: pd.DataFrame,
    logger: logging.Logger | None = None,
) -> pd.DataFrame:
    logger = logger or logging.getLogger(__name__)
    result = _merge_sales(inventory_df, sales_summary_df)
    result = _add_inventory_fields(result, logger)
    return _select_report_columns(result)
