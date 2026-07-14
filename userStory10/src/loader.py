"""CSV loading helpers."""
from pathlib import Path
import pandas as pd

CUSTOMER_COLUMNS = {"customer_id", "customer_name", "email", "status", "signup_date"}
ORDER_COLUMNS = {"order_id", "customer_id", "order_date", "order_amount", "order_status"}

def _load_csv(path: str | Path, required_columns: set[str]) -> pd.DataFrame:
    frame = pd.read_csv(path, dtype=str)
    missing = required_columns.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns in {path}: {sorted(missing)}")
    return frame

def load_customers(path: str | Path) -> pd.DataFrame:
    return _load_csv(path, CUSTOMER_COLUMNS)

def load_orders(path: str | Path) -> pd.DataFrame:
    return _load_csv(path, ORDER_COLUMNS)
