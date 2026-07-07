from pathlib import Path

import pandas as pd


def load_inventory(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path)


def load_sales_transactions(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path)
