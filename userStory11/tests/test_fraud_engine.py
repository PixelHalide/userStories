import pandas as pd

from src.fraud_engine import apply_fraud_rules
from tests.conftest import make_validated_transactions


def process(transaction, merchants):
    return apply_fraud_rules(transaction, merchants).iloc[0]


def test_high_value_transaction_flag(merchants):
    result = process(make_validated_transactions(transaction_amount="100000.01"), merchants)
    assert result["transaction_status"] == "SUSPICIOUS"
    assert "HIGH_VALUE_TRANSACTION" in result["fraud_reason"]


def test_cross_border_transaction_flag(merchants):
    result = process(make_validated_transactions(country="USA"), merchants)
    assert "CROSS_BORDER_TRANSACTION" in result["fraud_reason"]


def test_crypto_high_value_flag(merchants):
    result = process(
        make_validated_transactions(transaction_amount="50000.01", payment_method="CRYPTO"),
        merchants,
    )
    assert "CRYPTO_HIGH_VALUE" in result["fraud_reason"]


def test_multiple_fraud_rules_trigger(merchants):
    result = process(
        make_validated_transactions(
            transaction_amount="150000", payment_method="CRYPTO", country="USA"
        ),
        merchants,
    )
    assert bool(result["fraud_flag"]) is True
    assert result["fraud_reason"].split(";") == [
        "HIGH_VALUE_TRANSACTION",
        "CROSS_BORDER_TRANSACTION",
        "CRYPTO_HIGH_VALUE",
    ]


def test_rapid_transactions_flagged(merchants):
    times = ["10:00:00", "10:00:30", "10:01:00", "10:02:00"]
    transactions = pd.concat(
        [
            make_validated_transactions(
                transaction_id=f"T{index}", transaction_time=f"2024-06-01 {time}"
            )
            for index, time in enumerate(times)
        ],
        ignore_index=True,
    )
    results = apply_fraud_rules(transactions, merchants)
    assert results["fraud_reason"].str.contains("RAPID_TRANSACTIONS").all()


def test_transactions_outside_window_not_flagged(merchants):
    times = ["10:00:00", "10:00:30", "10:01:00", "10:02:01"]
    transactions = pd.concat(
        [
            make_validated_transactions(
                transaction_id=f"T{index}", transaction_time=f"2024-06-01 {time}"
            )
            for index, time in enumerate(times)
        ],
        ignore_index=True,
    )
    results = apply_fraud_rules(transactions, merchants)
    assert ~results["fraud_reason"].str.contains("RAPID_TRANSACTIONS").any()


def test_clean_transaction_is_valid(merchants):
    result = process(make_validated_transactions(), merchants)
    assert bool(result["fraud_flag"]) is False
    assert result["fraud_reason"] == ""
    assert result["transaction_status"] == "VALID"
