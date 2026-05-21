from pathlib import Path

from src.employee_scraper.scraper import (
    DEFAULT_EMPLOYEES_URL,
    add_salary_conversion,
    fetch_employees,
    normalize_employees,
)


def main() -> int:
    employees = normalize_employees(fetch_employees(DEFAULT_EMPLOYEES_URL))
    employees = add_salary_conversion(employees, "inr")
    output_path = Path("output/employees_normalized.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    employees.to_json(output_path, orient="records", indent=2)
    print(f"Wrote {len(employees)} employees to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
