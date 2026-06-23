from pathlib import Path

import pandas as pd


LOOKUP_COLUMN = "lookup_key"


def map_data(raw_data_path: str | Path, reference_data_path: str | Path) -> pd.DataFrame:
    """Return reference rows whose lookup key appears in the raw data."""
    raw_data = pd.read_csv(raw_data_path)
    reference_data = pd.read_excel(reference_data_path)

    for name, data in (("raw data", raw_data), ("reference data", reference_data)):
        if LOOKUP_COLUMN not in data.columns:
            raise ValueError(f"Missing '{LOOKUP_COLUMN}' column in {name}")

    lookup_values = raw_data[LOOKUP_COLUMN].dropna().drop_duplicates()
    mapped_data = reference_data[reference_data[LOOKUP_COLUMN].isin(lookup_values)]

    return mapped_data.drop_duplicates(subset=[LOOKUP_COLUMN]).copy()


def save_mapped_output(
    raw_data_path: str | Path,
    reference_data_path: str | Path,
    output_path: str | Path,
) -> Path:
    """Map the input data and save it as a CSV file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    map_data(raw_data_path, reference_data_path).to_csv(output_path, index=False)
    return output_path
