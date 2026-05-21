
import os
import logging
import json
import re
import time
from datetime import date, datetime
from io import StringIO
from typing import Any
import dotenv
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import pandas as pd

dotenv.load_dotenv(override=True)


DEFAULT_EMPLOYEES_URL = (
    "https://api.slingacademy.com/v1/sample-data/files/employees.json"
)
DEFAULT_CURRENCY_URL = (
    "https://api.currencyapi.com/v3/latest"
    "?apikey="
    f"{os.getenv('API_KEY')}"
)

EXPECTED_FIELDS = {
    "id",
    "first_name",
    "last_name",
    "email",
    "phone",
    "gender",
    "age",
    "job_title",
    "years_of_experience",
    "salary",
    "department",
}

OUTPUT_FIELDS = [
    "employee_id",
    "Full Name",
    "email",
    "phone",
    "gender",
    "age",
    "job_title",
    "years_of_experience",
    "salary",
    "department",
    "designation",
]

logger = logging.getLogger(__name__)


class EmployeeScraperError(RuntimeError):
    pass


def fetch_employees(
    url: str = DEFAULT_EMPLOYEES_URL,
    retries: int = 3,
    timeout: float = 10.0,
) -> list[dict[str, Any]]:
    "Scrape employee data from API and return list of employee records"
    last_error: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            request = Request(url, headers={"Accept": "application/json"})
            with urlopen(request, timeout=timeout) as response:
                status_code = response.getcode()
                if status_code != 200:
                    message = f"API returned non-200 status code: {status_code}"
                    logger.error(message)
                    raise EmployeeScraperError(message)

                payload = response.read().decode("utf-8")
                records = pd.read_json(StringIO(payload)).to_dict("records")
                return extract_employee_records(records)
        except HTTPError as exc:
            message = f"API returned non-200 status code: {exc.code}"
            logger.error(message)
            raise EmployeeScraperError(message) from exc
        except (TimeoutError, URLError, ValueError) as exc:
            last_error = exc
            logger.warning("Attempt %s/%s failed: %s", attempt, retries, exc)
            if attempt < retries:
                time.sleep(0.5)

    message = f"Failed to fetch employee data after {retries} attempts"
    logger.error(message)
    raise EmployeeScraperError(message) from last_error


def extract_employee_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        records = payload
    elif isinstance(payload, dict):
        records = (
            payload.get("employees")
            or payload.get("data")
            or payload.get("records")
        )
    else:
        records = None

    if not isinstance(records, list):
        raise EmployeeScraperError("JSON response does not contain employee records")
    if not all(isinstance(record, dict) for record in records):
        raise EmployeeScraperError("Employee records must be JSON objects")

    return records


def normalize_employees(records: list[dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(records)
    validate_columns(df)

    df = df.copy()
    df["employee_id"] = df["id"].astype(int)
    df["Full Name"] = (
        df["first_name"].astype(str).str.strip()
        + " "
        + df["last_name"].astype(str).str.strip()
    ).str.strip()
    df["email"] = df["email"].astype(str)
    df["phone"] = df["phone"].apply(normalize_phone)
    df["gender"] = df["gender"].astype(str)
    df["age"] = df["age"].astype(int)
    df["job_title"] = df["job_title"].astype(str)
    df["years_of_experience"] = df["years_of_experience"].astype(int)
    df["salary"] = df["salary"].astype(int)
    df["department"] = df["department"].astype(str)
    df["designation"] = df["years_of_experience"].apply(get_designation)

    output_fields = OUTPUT_FIELDS.copy()
    if "hire_date" in df.columns:
        df["hire_date"] = df["hire_date"].apply(normalize_date)
        output_fields.append("hire_date")

    return df[output_fields]


def add_salary_conversion(
    df: pd.DataFrame,
    target_currency: str,
    currency_url: str = DEFAULT_CURRENCY_URL,
) -> pd.DataFrame:
    rate = fetch_currency_rate(target_currency, currency_url)
    df = df.copy()
    df["salary"] = (df["salary"].astype(float) * rate).round().astype(int)
    df["salary_currency"] = target_currency.upper()
    return df


def fetch_currency_rate(
    target_currency: str,
    currency_url: str = DEFAULT_CURRENCY_URL,
    timeout: float = 10.0,
) -> float:
    request = Request(currency_url, headers={"Accept": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        status_code = response.getcode()
        if status_code != 200:
            message = f"Currency API returned non-200 status code: {status_code}"
            logger.error(message)
            raise EmployeeScraperError(message)

        payload = json.loads(response.read().decode("utf-8"))
        data = payload.get("data", {})
        currency = target_currency.upper()

        if currency not in data:
            raise EmployeeScraperError(f"Currency not found: {currency}")
        return float(data[currency]["value"])


def validate_columns(df: pd.DataFrame) -> None:
    missing_columns = EXPECTED_FIELDS - set(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise EmployeeScraperError(f"Employee record is missing fields: {missing}")


def get_designation(years_of_experience: int) -> str:
    "Return designation based on years of experience"
    if years_of_experience < 3:
        return "system engineer"
    if years_of_experience <= 5:
        return "data engineer"
    if years_of_experience <= 10:
        return "senior data engineer"
    return "lead"


def normalize_phone(phone: Any) -> int | str:
    "Remove non-digit chars from phone number and convert to int"
    phone_text = str(phone)
    if "x" in phone_text.lower():
        return "Invalid Number"

    digits = re.sub(r"\D", "", phone_text)
    if not digits:
        raise EmployeeScraperError("Phone number does not contain digits")
    return int(digits)


def normalize_date(value: Any) -> str:
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()

    date_text = str(value).strip()
    for date_format in ("%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(date_text, date_format).date().isoformat()
        except ValueError:
            continue

    raise EmployeeScraperError(f"Unsupported date format: {value}")
