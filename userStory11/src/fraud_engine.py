"""Pandas-based rule engine for transaction fraud detection."""

from __future__ import annotations

import pandas as pd

HIGH_VALUE_TRANSACTION = "HIGH_VALUE_TRANSACTION"
CROSS_BORDER_TRANSACTION = "CROSS_BORDER_TRANSACTION"
RAPID_TRANSACTIONS = "RAPID_TRANSACTIONS"
CRYPTO_HIGH_VALUE = "CRYPTO_HIGH_VALUE"
RAPID_WINDOW = pd.Timedelta(minutes=2)


def find_rapid_transaction_ids(transactions: pd.DataFrame) -> set[str]:
    """Return IDs that participate in a 4+ transaction customer window."""
    rapid_ids: set[str] = set()
    for _, customer_rows in transactions.groupby("customer_id", sort=False):
        ordered = customer_rows.sort_values("transaction_time")
        for _, first_transaction in ordered.iterrows():
            window_end = first_transaction["transaction_time"] + RAPID_WINDOW
            transactions_in_window = ordered[
                ordered["transaction_time"].between(
                    first_transaction["transaction_time"], window_end
                )
            ]
            if len(transactions_in_window) > 3:
                rapid_ids.update(transactions_in_window["transaction_id"])
    return rapid_ids


def apply_fraud_rules(transactions: pd.DataFrame, merchants: pd.DataFrame) -> pd.DataFrame:
    """Apply every fraud rule and return an annotated DataFrame."""
    frame = transactions.copy()
    merchant_country = (
        merchants.drop_duplicates("merchant_id", keep="last").set_index("merchant_id")["country"]
    )
    rapid_ids = find_rapid_transaction_ids(frame)

    def fraud_reasons(transaction: pd.Series) -> str:
        reasons = []
        if transaction["transaction_amount"] > 100000:
            reasons.append(HIGH_VALUE_TRANSACTION)
        merchant_home_country = merchant_country[transaction["merchant_id"]]
        if transaction["country"].casefold() != merchant_home_country.casefold():
            reasons.append(CROSS_BORDER_TRANSACTION)
        if transaction["transaction_id"] in rapid_ids:
            reasons.append(RAPID_TRANSACTIONS)
        if (
            transaction["payment_method"].upper() == "CRYPTO"
            and transaction["transaction_amount"] > 50000
        ):
            reasons.append(CRYPTO_HIGH_VALUE)
        return ";".join(reasons)

    frame["fraud_reason"] = frame.apply(fraud_reasons, axis=1)
    frame["fraud_flag"] = frame["fraud_reason"].ne("")
    frame["transaction_status"] = frame["fraud_flag"].map(
        {True: "SUSPICIOUS", False: "VALID"}
    )
    return frame
