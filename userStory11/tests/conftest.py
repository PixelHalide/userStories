import pandas as pd
import pytest


@pytest.fixture
def merchants():
    return pd.DataFrame(
        [
            {
                "merchant_id": "M1",
                "merchant_name": "Active Shop",
                "merchant_category": "Retail",
                "country": "India",
                "status": "ACTIVE",
            },
            {
                "merchant_id": "M2",
                "merchant_name": "Blocked Shop",
                "merchant_category": "Retail",
                "country": "USA",
                "status": "BLOCKED",
            },
        ]
    )


def make_raw_transactions(**overrides):
    transaction = {
        "transaction_id": "T1",
        "merchant_id": "M1",
        "customer_id": "C1",
        "transaction_amount": "100.00",
        "transaction_time": "2024-06-01 10:00:00",
        "payment_method": "CARD",
        "country": "India",
    }
    transaction.update(overrides)
    return pd.DataFrame([transaction])


def make_validated_transactions(**overrides):
    frame = make_raw_transactions(**overrides)
    frame["transaction_amount"] = pd.to_numeric(frame["transaction_amount"])
    frame["transaction_time"] = pd.to_datetime(frame["transaction_time"])
    return frame

