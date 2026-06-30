import logging

import pandas as pd


logger = logging.getLogger(__name__)
USAGE_COLUMNS = ["subscription_id", "total_usage_gb"]
REQUIRED_COLUMNS = ["subscription_id", "usage_date", "data_used_gb"]


def aggregate_usage(usage_df, month="2024-03"):
    """Aggregate valid usage records for a target month by subscription."""
    cleaned_usage = clean_usage_data(usage_df)
    if cleaned_usage.empty:
        return pd.DataFrame(columns=USAGE_COLUMNS)

    target_period = pd.Period(month, freq="M")
    monthly_usage = cleaned_usage[
        cleaned_usage["usage_date"].dt.to_period("M") == target_period
    ]

    aggregated_usage = monthly_usage.groupby("subscription_id", as_index=False)["data_used_gb"].sum()
    aggregated_usage.columns = USAGE_COLUMNS # type: ignore
    return aggregated_usage


def clean_usage_data(usage_df):
    """Validate and normalize usage records before aggregation."""
    if not has_valid_usage_input(usage_df):
        return pd.DataFrame(columns=REQUIRED_COLUMNS)

    data = usage_df.copy()
    data["usage_date"] = pd.to_datetime(data["usage_date"], format="%Y-%m-%d", errors="coerce")

    invalid_dates = data["usage_date"].isna()
    if invalid_dates.any():
        logger.warning("Skipping %d usage records with invalid dates", invalid_dates.sum())

    data["data_used_gb"] = pd.to_numeric(data["data_used_gb"], errors="coerce").fillna(0)

    negative_usage = data["data_used_gb"] < 0
    if negative_usage.any():
        logger.warning("Skipping %d usage records with negative usage", negative_usage.sum())

    return data[data["usage_date"].notna() & ~negative_usage]


def has_valid_usage_input(usage_df):
    """Check whether usage input is present and has the required schema."""
    if usage_df is None or usage_df.empty:
        return False

    missing_columns = set(REQUIRED_COLUMNS) - set(usage_df.columns)
    if missing_columns:
        logger.error("Usage data is missing required columns: %s", sorted(missing_columns))
        return False

    return True
