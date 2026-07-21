import json

import pandas as pd
import pytest

from src.loader import load_merchants, load_transactions
from src.main import run_pipeline
from src.reporter import build_fraud_summary, write_reports


def test_loaders_and_missing_columns(tmp_path):
    merchants_file = tmp_path / "merchants.csv"
    merchants_file.write_text(
        "merchant_id,merchant_name,merchant_category,country,status\nM1,Shop,Retail,India,ACTIVE\n",
        encoding="utf-8",
    )
    transactions_file = tmp_path / "transactions.csv"
    transactions_file.write_text(
        "transaction_id,merchant_id,customer_id,transaction_amount,transaction_time,payment_method,country\n"
        "T1,M1,C1,1,2024-06-01 10:00:00,CARD,India\n",
        encoding="utf-8",
    )
    assert load_merchants(merchants_file).iloc[0]["merchant_name"] == "Shop"
    assert load_transactions(transactions_file).iloc[0]["transaction_id"] == "T1"

    bad_file = tmp_path / "bad.csv"
    bad_file.write_text("merchant_id\nM1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing required columns"):
        load_merchants(bad_file)


def test_reports_have_required_schema_and_summary(tmp_path):
    transactions = pd.DataFrame(
        [
            {
                "transaction_id": "T1",
                "merchant_id": "M1",
                "customer_id": "C1",
                "transaction_amount": 120000.0,
                "transaction_time": pd.Timestamp("2024-06-01 10:00:00"),
                "fraud_flag": True,
                "fraud_reason": "HIGH_VALUE_TRANSACTION;CROSS_BORDER_TRANSACTION;RAPID_TRANSACTIONS",
                "transaction_status": "SUSPICIOUS",
            }
        ]
    )
    settlements = pd.DataFrame(
        [
            {
                "merchant_id": "M1",
                "merchant_name": "Shop",
                "total_transactions": 1,
                "valid_transactions": 0,
                "fraud_transactions": 1,
                "settlement_amount": 0.0,
            }
        ]
    )
    summary = write_reports(transactions, settlements, tmp_path)
    assert summary == build_fraud_summary(transactions)
    assert summary["fraud_transactions"] == 1
    assert summary["high_value_frauds"] == 1
    assert summary["cross_border_frauds"] == 1
    assert summary["rapid_transaction_frauds"] == 1

    row = pd.read_csv(tmp_path / "processed_transactions.csv").iloc[0]
    assert bool(row["fraud_flag"]) is True
    with (tmp_path / "fraud_summary.json").open() as handle:
        assert json.load(handle) == summary


def test_pipeline_handles_bad_data_end_to_end(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    (data / "merchants.csv").write_text(
        "merchant_id,merchant_name,merchant_category,country,status\nM1,Shop,Retail,India,ACTIVE\n",
        encoding="utf-8",
    )
    (data / "transactions.csv").write_text(
        "transaction_id,merchant_id,customer_id,transaction_amount,transaction_time,payment_method,country\n"
        "T1,M1,C1,25,2024-06-01 10:00:00,CARD,India\n"
        "T2,M9,C2,25,2024-06-01 10:00:00,CARD,India\n",
        encoding="utf-8",
    )
    summary = run_pipeline(tmp_path)
    assert summary["total_transactions"] == 1
    assert (tmp_path / "logs" / "fraud_engine.log").exists()
    assert (tmp_path / "outputs" / "merchant_settlement_report.csv").exists()
