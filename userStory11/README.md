# Payment Transaction Fraud Detection & Settlement Engine

This pandas-based Python application loads merchant and payment transaction CSV files, rejects
invalid records, applies rule-based fraud checks, settles valid transactions, and
writes auditable CSV and JSON reports. DataFrames are used throughout loading,
validation, fraud analysis, aggregation, and reporting.

## Business rules

A record is rejected and logged when its merchant is unknown or blocked, its
amount is zero/negative/not numeric, or its timestamp is not in
`YYYY-MM-DD HH:MM:SS` format. Rejected records do not appear in reports or metrics.

A validated transaction is `SUSPICIOUS` when one or more of these rules applies:

- `HIGH_VALUE_TRANSACTION`: amount is greater than 100,000.
- `CROSS_BORDER_TRANSACTION`: transaction and merchant countries differ.
- `RAPID_TRANSACTIONS`: the customer has at least four transactions in an
  inclusive two-minute window.
- `CRYPTO_HIGH_VALUE`: payment method is CRYPTO and amount is greater than 50,000.

Every transaction participating in a qualifying rapid window is flagged. Multiple
reasons are retained in deterministic, semicolon-separated order. Only `VALID`
transactions contribute to a merchant's settlement amount.

## Run the program

From the `userStory11` directory:

```bash
python3 -m src.main
```

Inputs are read from `data/`. Outputs are written to:

- `outputs/processed_transactions.csv`
- `outputs/merchant_settlement_report.csv`
- `outputs/fraud_summary.json`
- `logs/fraud_engine.log`

## Run tests

```bash
python3 -m pip install -r requirements.txt
python3 -m pytest
```

The pytest configuration enforces at least 80% line coverage for `src`.
