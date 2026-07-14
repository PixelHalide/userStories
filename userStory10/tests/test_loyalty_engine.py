import unittest
import pandas as pd
from src.loyalty_engine import add_customer_classifications, classify_activity, classify_loyalty

class TestLoyaltyEngine(unittest.TestCase):
    def test_platinum_customer_classification(self):
        self.assertEqual(classify_loyalty(10000), "PLATINUM")
    def test_gold_customer_classification(self):
        self.assertEqual(classify_loyalty(5000), "GOLD")
    def test_silver_customer_classification(self):
        self.assertEqual(classify_loyalty(1000), "SILVER")
    def test_bronze_customer_classification(self):
        self.assertEqual(classify_loyalty(999.99), "BRONZE")
    def test_active_customer_with_orders(self):
        self.assertEqual(classify_activity("ACTIVE", 1), "ACTIVE_CUSTOMER")
    def test_active_customer_without_orders(self):
        self.assertEqual(classify_activity("ACTIVE", 0), "INACTIVE_CUSTOMER")
    def test_inactive_customer_status(self):
        self.assertEqual(classify_activity("INACTIVE", 10), "INACTIVE_CUSTOMER")
    def test_classifications_are_added_to_dataframe(self):
        frame = pd.DataFrame([{"status": "ACTIVE", "total_orders": 1, "total_spent": 5000}])
        result = add_customer_classifications(frame)
        self.assertEqual(result.loc[0, "loyalty_segment"], "GOLD")
        self.assertEqual(result.loc[0, "customer_activity_status"], "ACTIVE_CUSTOMER")

if __name__ == "__main__":
    unittest.main()
