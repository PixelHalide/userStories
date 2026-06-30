def evaluate_status(previous_status, total_usage_gb, usage_limit_gb):
    """Evaluate the final subscription status after monthly usage is known."""
    previous_status = str(previous_status).upper()

    if previous_status == "CANCELLED":
        return "CANCELLED"

    if usage_limit_gb > 0 and total_usage_gb > (usage_limit_gb * 1.5):
        return "SUSPENDED"

    if previous_status == "SUSPENDED" and total_usage_gb <= usage_limit_gb:
        return "ACTIVE"

    return previous_status
