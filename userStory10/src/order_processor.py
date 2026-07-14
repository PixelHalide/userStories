"""Order validation and per-customer aggregation."""
import logging
import pandas as pd

def valid_delivered_orders(orders: pd.DataFrame, known_customer_ids: set[str], logger: logging.Logger | None = None) -> pd.DataFrame:
    """Return valid delivered orders from May 2024."""
    log = logger or logging.getLogger(__name__)
    clean = orders.copy()
    clean["parsed_date"] = pd.to_datetime(clean["order_date"], errors="coerce")
    clean["numeric_amount"] = pd.to_numeric(clean["order_amount"], errors="coerce")
    invalid_dates = clean["parsed_date"].isna()
    for order_id in clean.loc[invalid_dates, "order_id"]:
        log.warning("Order %s skipped: invalid order date", order_id)
    invalid_amounts = clean["numeric_amount"].isna() | (clean["numeric_amount"] < 0)
    for order_id in clean.loc[invalid_amounts, "order_id"]:
        log.warning("Order %s skipped: invalid or negative amount", order_id)
    unknown_customers = ~clean["customer_id"].isin(known_customer_ids)
    for customer_id in clean.loc[unknown_customers, "customer_id"].drop_duplicates():
        log.warning("Orders skipped for unknown customer ID: %s", customer_id)
    in_may = (clean["parsed_date"].dt.year == 2024) & (clean["parsed_date"].dt.month == 5)
    delivered = clean["order_status"].str.strip().str.upper().eq("DELIVERED")
    return clean.loc[~invalid_dates & ~invalid_amounts & ~unknown_customers & in_may & delivered].copy()

def aggregate_customer_orders(customers: pd.DataFrame, orders: pd.DataFrame, logger: logging.Logger | None = None) -> pd.DataFrame:
    """Attach delivered-order metrics to every customer."""
    valid = valid_delivered_orders(orders, set(customers["customer_id"].astype(str)), logger)
    if valid.empty:
        metrics = pd.DataFrame(columns=["customer_id", "total_orders", "total_spent"])
    else:
        metrics = valid.groupby("customer_id", as_index=False).agg(
            total_orders=("order_id", "count"), total_spent=("numeric_amount", "sum")
        )
    result = customers.merge(metrics, on="customer_id", how="left")
    result["total_orders"] = result["total_orders"].fillna(0).astype(int)
    result["total_spent"] = result["total_spent"].fillna(0.0).astype(float).round(2)
    result["average_order_value"] = result["total_spent"].div(
        result["total_orders"].replace(0, pd.NA)
    ).fillna(0.0).astype(float).round(2)
    return result
