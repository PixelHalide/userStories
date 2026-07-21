import pandas as pd

from src.settlement_engine import calculate_settlements
from tests.conftest import make_validated_transactions


def settled_transaction(status="VALID", **overrides):
    frame = make_validated_transactions(**overrides)
    frame["transaction_status"] = status
    return frame


def test_settlement_only_valid_transactions(merchants):
    transactions = pd.concat(
        [
            settled_transaction("VALID", transaction_id="T1", transaction_amount="100"),
            settled_transaction("SUSPICIOUS", transaction_id="T2", transaction_amount="900"),
        ],
        ignore_index=True,
    )
    row = calculate_settlements(transactions, merchants).iloc[0]
    assert row["total_transactions"] == 2
    assert row["valid_transactions"] == 1
    assert row["fraud_transactions"] == 1
    assert row["settlement_amount"] == 100.0


def test_settlement_amount_calculation(merchants):
    transactions = pd.concat(
        [
            settled_transaction(transaction_id="T1", transaction_amount="10.25"),
            settled_transaction(transaction_id="T2", transaction_amount="20.75"),
        ],
        ignore_index=True,
    )
    row = calculate_settlements(transactions, merchants).iloc[0]
    assert row["settlement_amount"] == 31.0
