import pandas as pd

REQUIRED_FIELDS = ["User Id", "First Name", "Last Name", "Sex", "Email", "Phone", "Date of birth", "Job Title"]

def map_data(file_path):
    file_path = str(file_path)

    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith((".xls", ".xlsx")):
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file type. Only CSV and Excel files are allowed.")

    missing_fields = [field for field in REQUIRED_FIELDS if field not in df.columns]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

    return df[REQUIRED_FIELDS]
