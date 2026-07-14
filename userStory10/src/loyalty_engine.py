"""Customer loyalty and activity classification."""
import pandas as pd

def classify_loyalty(total_spent: float) -> str:
    if total_spent >= 10_000:
        return "PLATINUM"
    if total_spent >= 5_000:
        return "GOLD"
    if total_spent >= 1_000:
        return "SILVER"
    return "BRONZE"

def classify_activity(customer_status: str, total_orders: int) -> str:
    if str(customer_status).strip().upper() == "ACTIVE" and total_orders > 0:
        return "ACTIVE_CUSTOMER"
    return "INACTIVE_CUSTOMER"

def add_customer_classifications(customers: pd.DataFrame) -> pd.DataFrame:
    result = customers.copy()
    result["loyalty_segment"] = result["total_spent"].apply(classify_loyalty)
    result["customer_activity_status"] = result.apply(
        lambda row: classify_activity(row["status"], row["total_orders"]), axis=1
    )
    return result
