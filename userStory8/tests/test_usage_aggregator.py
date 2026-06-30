import unittest

import pandas as pd

from userStory8.src.usage_aggregator import aggregate_usage


class TestUsageAggregator(unittest.TestCase):
    def test_multiple_usage_records(self):
        usage_df = pd.DataFrame(
            [
                {"subscription_id": "S001", "usage_date": "2024-03-01", "data_used_gb": 20},
                {"subscription_id": "S001", "usage_date": "2024-03-15", "data_used_gb": 30},
                {"subscription_id": "S002", "usage_date": "2024-03-20", "data_used_gb": 10},
            ]
        )

        result = aggregate_usage(usage_df)

        s001_usage = result.loc[result["subscription_id"] == "S001", "total_usage_gb"].iloc[0]
        self.assertEqual(s001_usage, 50)

    def test_no_usage_records(self):
        usage_df = pd.DataFrame(columns=["subscription_id", "usage_date", "data_used_gb"])

        result = aggregate_usage(usage_df)

        self.assertTrue(result.empty)
        self.assertEqual(list(result.columns), ["subscription_id", "total_usage_gb"])

    def test_invalid_usage_dates(self):
        usage_df = pd.DataFrame(
            [
                {"subscription_id": "S001", "usage_date": "invalid_date", "data_used_gb": 20},
                {"subscription_id": "S001", "usage_date": "2024-03-15", "data_used_gb": 30},
                {"subscription_id": "S001", "usage_date": "2024-04-01", "data_used_gb": 100},
            ]
        )

        with self.assertLogs("userStory8.src.usage_aggregator", level="WARNING"):
            result = aggregate_usage(usage_df)

        self.assertEqual(len(result), 1)
        self.assertEqual(result["total_usage_gb"].iloc[0], 30)

    def test_negative_usage_records_are_skipped(self):
        usage_df = pd.DataFrame(
            [
                {"subscription_id": "S001", "usage_date": "2024-03-01", "data_used_gb": 20},
                {"subscription_id": "S001", "usage_date": "2024-03-02", "data_used_gb": -5},
            ]
        )

        with self.assertLogs("userStory8.src.usage_aggregator", level="WARNING"):
            result = aggregate_usage(usage_df)

        self.assertEqual(result["total_usage_gb"].iloc[0], 20)

    def test_missing_usage_columns_returns_empty_result(self):
        usage_df = pd.DataFrame([{"subscription_id": "S001"}])

        with self.assertLogs("userStory8.src.usage_aggregator", level="ERROR"):
            result = aggregate_usage(usage_df)

        self.assertTrue(result.empty)
        self.assertEqual(list(result.columns), ["subscription_id", "total_usage_gb"])


if __name__ == "__main__":
    unittest.main()
