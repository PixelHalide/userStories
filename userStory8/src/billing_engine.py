import logging


logger = logging.getLogger(__name__)


def calculate_bill(monthly_fee, usage_limit_gb, total_usage_gb, status):
    """Calculate overage and final bill for one subscription."""
    monthly_fee = _safe_number(monthly_fee, "monthly_fee")
    usage_limit_gb = _safe_number(usage_limit_gb, "usage_limit_gb")
    total_usage_gb = _safe_number(total_usage_gb, "total_usage_gb")
    normalized_status = str(status).upper()

    if normalized_status == "CANCELLED":
        return 0.0, 0.0

    overage_gb = max(total_usage_gb - usage_limit_gb, 0.0)

    if normalized_status == "SUSPENDED":
        return overage_gb, monthly_fee

    return overage_gb, monthly_fee + (overage_gb * 10)


def _safe_number(value, field_name):
    try:
        if value is None:
            raise ValueError("missing value")
        return float(value)
    except (TypeError, ValueError):
        logger.warning("Invalid numeric value for %s: %r. Defaulting to 0.", field_name, value)
        return 0.0
