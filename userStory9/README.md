Inventory Reconciliation and Sales Analysis Engine
==================================================

Project Overview
----------------

This is a simple pandas-based Python project that reads inventory and sales CSV files, reconciles stock after April 2024 sales, logs invalid data, and writes:

- `inventory_reconciliation.csv`
- `sales_summary.json`

Business Rules
--------------

- Only sales transactions dated in April 2024 are processed.
- Invalid dates are skipped and logged.
- Negative quantities are skipped and logged.
- Sales for unknown `product_id` values are skipped and logged.
- `final_stock = current_stock - total_sold_quantity`.
- If stock would become negative, final stock is set to `0` and a `STOCK_ERROR` is logged.
- Stock status values:
  - `OUT_OF_STOCK` when final stock is `0`
  - `LOW_STOCK` when final stock is from `1` to `10`
  - `AVAILABLE` when final stock is greater than `10`

Execution Steps
---------------

From the `userStory9` folder:

```bash
python3 -m src.main
```

Test Execution Steps
--------------------

Run tests with coverage printed:

```bash
python3 run_tests.py
```

Assumptions and Edge Cases
--------------------------

- Input files are expected at `data/inventory.csv` and `data/sales_transactions.csv`.
- The application uses pandas for CSV loading, filtering, aggregation, and reconciliation.
- Bad rows are skipped instead of crashing the application.
- Unknown products do not contribute to sales totals.
- Output reports are written in the project root.
