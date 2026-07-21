import logging

import pandas as pd

from src.validator import validate_transactions
from tests.conftest import make_raw_transactions


def test_invalid_merchant_rejected(merchants, caplog):
    with caplog.at_level(logging.ERROR):
        result = validate_transactions(make_raw_transactions(merchant_id="M999"), merchants)
    assert result.empty
    assert "unknown merchant" in caplog.text


def test_blocked_merchant_rejected(merchants, caplog):
    with caplog.at_level(logging.ERROR):
        result = validate_transactions(make_raw_transactions(merchant_id="M2"), merchants)
    assert result.empty
    assert "blocked merchant" in caplog.text


def test_negative_amount_rejected(merchants, caplog):
    with caplog.at_level(logging.ERROR):
        result = validate_transactions(make_raw_transactions(transaction_amount="-1"), merchants)
    assert result.empty
    assert "positive finite number" in caplog.text


def test_invalid_timestamp_handling(merchants, caplog):
    with caplog.at_level(logging.ERROR):
        result = validate_transactions(make_raw_transactions(transaction_time="not-a-time"), merchants)
    assert result.empty
    assert "invalid transaction timestamp" in caplog.text


def test_valid_transaction_is_normalized(merchants):
    result = validate_transactions(make_raw_transactions(), merchants)
    assert len(result) == 1
    assert result.loc[0, "transaction_amount"] == 100.0
    assert result.loc[0, "transaction_time"] == pd.Timestamp("2024-06-01 10:00:00")


def test_non_numeric_and_non_finite_amounts_rejected(merchants):
    assert validate_transactions(make_raw_transactions(transaction_amount="abc"), merchants).empty
    assert validate_transactions(make_raw_transactions(transaction_amount="inf"), merchants).empty
