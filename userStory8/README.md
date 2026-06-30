# Subscription Billing & Status Evaluation Engine

## Project overview

This project processes subscription and usage CSV files for March 2024, calculates monthly bills, evaluates final subscription statuses, and writes:

- `billing_output.csv`
- `billing_summary.json`
- `logs/billing.log`

The implementation uses simple Python with pandas and keeps the logic split across small modules in `src/`.

## Business rules

- Usage is aggregated per subscription for March 2024 only.
- Invalid usage dates are skipped and logged.
- Missing numeric usage values default to `0`.
- Negative usage records are treated as invalid and skipped.
- Active subscriptions pay the monthly fee plus `10` per GB over the plan limit.
- Suspended subscriptions pay only the monthly fee, with no overage charge.
- Cancelled subscriptions are billed `0`.
- Usage above `150%` of the plan limit changes the final status to `SUSPENDED`.
- A previously suspended subscription returns to `ACTIVE` when usage is less than or equal to the limit.
- Cancelled subscriptions always remain `CANCELLED`.

## How to run the application

From the repository root:

```bash
python3 -m userStory8.src.main
```

Output files are written in the `userStory8` folder:

```text
userStory8/billing_output.csv
userStory8/billing_summary.json
userStory8/logs/billing.log
```

## How to run unit tests

From the repository root:

```bash
python3 -m userStory8.run_tests
```

This runs all unit tests and prints the coverage percentage. The coverage check fails if coverage is below `80%`.

To run only the unit tests without coverage:

```bash
python3 -m unittest discover -s userStory8/tests
```

## Assumptions made

- The target billing month is fixed to March 2024.
- Cancelled subscriptions are included in the output and summary with a bill of `0` because the summary requires cancelled counts.
- The required processing rule says subscriptions that are not cancelled should be billed; the billing rule also defines cancelled billing as `0`, so cancelled records are retained for reporting.
- Negative usage is invalid data and is skipped.
- Missing numeric values in subscriptions default to `0` so processing can continue safely.

## Edge cases handled

- Invalid dates in usage data.
- Usage outside March 2024.
- Empty usage files.
- Subscriptions with no usage records.
- Missing or invalid numeric values.
- Cancelled status staying unchanged.
- Suspended subscriptions receiving no overage charge.
