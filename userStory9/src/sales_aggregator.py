import logging

import pandas as pd


APRIL_2024_START = pd.Timestamp("2024-04-01")
MAY_2024_START = pd.Timestamp("2024-05-01")


def _parse_transaction_dates(sales: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    sales = sales.copy()
    sales["parsed_date"] = pd.to_datetime(sales["transaction_date"], format="%Y-%m-%d", errors="coerce")

    invalid_dates = sales[sales["parsed_date"].isna()]
    for _, row in invalid_dates.iterrows():
        logger.warning("Invalid date skipped: transaction_id=%s date=%s", row["transaction_id"], row["transaction_date"])

    return sales


def _normalize_quantities(sales: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    sales = sales.copy()
    sales["quantity_sold"] = pd.to_numeric(sales["quantity_sold"], errors="coerce")

    negative_sales = sales[sales["quantity_sold"] < 0]
    for _, row in negative_sales.iterrows():
        logger.warning("Negative quantity ignored: transaction_id=%s quantity=%s", row["transaction_id"], row["quantity_sold"])

    return sales


def _filter_valid_april_sales(sales: pd.DataFrame) -> pd.DataFrame:
    return sales[
        (sales["parsed_date"] >= APRIL_2024_START)
        & (sales["parsed_date"] < MAY_2024_START)
        & (sales["quantity_sold"] >= 0)
    ].copy()


def _filter_known_products(
    sales: pd.DataFrame,
    inventory_df: pd.DataFrame,
    logger: logging.Logger,
) -> pd.DataFrame:
    known_products = set(inventory_df["product_id"])
    unknown_sales = sales[~sales["product_id"].isin(known_products)]

    for _, row in unknown_sales.iterrows():
        logger.warning("Unknown product ignored: transaction_id=%s product_id=%s", row["transaction_id"], row["product_id"])

    return sales[sales["product_id"].isin(known_products)]


def aggregate_april_sales(
    sales_df: pd.DataFrame,
    inventory_df: pd.DataFrame,
    logger: logging.Logger | None = None,
) -> tuple[pd.DataFrame, int]:
    logger = logger or logging.getLogger(__name__)
    sales = _parse_transaction_dates(sales_df, logger)
    sales = _normalize_quantities(sales, logger)
    april_sales = _filter_valid_april_sales(sales)
    valid_sales = _filter_known_products(april_sales, inventory_df, logger)

    if valid_sales.empty:
        return pd.DataFrame(columns=["product_id", "total_sold_quantity"]), 0

    summary = (
        valid_sales.groupby("product_id", as_index=False)["quantity_sold"]
        .sum()
        .rename(columns={"quantity_sold": "total_sold_quantity"})
    ) # type: ignore
    summary["total_sold_quantity"] = summary["total_sold_quantity"].astype(int)
    return summary, len(valid_sales)
