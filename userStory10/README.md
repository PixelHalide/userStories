# Customer Order Analytics & Loyalty Engine

A simple pandas application that validates May 2024 orders, aggregates delivered
orders for every customer, classifies loyalty/activity, and writes CSV/JSON output.

## Run

```bash
python3 -m src.main
```

Outputs are `customer_loyalty_report.csv`, `analytics_summary.json`, and
`logs/analytics.log`.

## Test with coverage

```bash
python3 run_tests.py
```

`total_orders` means valid delivered orders in May 2024. Cancelled, returned,
invalid, out-of-month, negative-amount, and unknown-customer orders do not affect
order count, revenue, average order value, or activity classification.
