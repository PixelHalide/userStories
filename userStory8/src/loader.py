import logging
from pathlib import Path

import pandas as pd


logger = logging.getLogger(__name__)


def load_csv(file_path):
    """Load a CSV file into a DataFrame without crashing the application."""
    path = Path(file_path)
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        logger.error("Input file not found: %s", path)
    except pd.errors.EmptyDataError:
        logger.error("Input file is empty: %s", path)
    except Exception as exc:
        logger.exception("Failed to load CSV file %s: %s", path, exc)

    return pd.DataFrame()
