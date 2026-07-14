import unittest
import pandas as pd
from src.order_processor import aggregate_customer_orders

class TestOrderProcessor(unittest.TestCase):
    def setUp(self):
        self.customers = pd.DataFrame([
            {"customer_id": "C1", "customer_name": "One", "status": "ACTIVE"},
            {"customer_id": "C2", "customer_name": "Two", "status": "ACTIVE"},
        ])

    def orders(self, rows):
        return pd.DataFrame(rows, columns=["order_id", "customer_id", "order_date", "order_amount", "order_status"])

    def test_customer_order_aggregation(self):
        orders = self.orders([
            ("O1", "C1", "2024-05-01", "1000", "DELIVERED"),
            ("O2", "C1", "2024-05-02", "500", "DELIVERED"),
            ("O3", "C1", "2024-05-03", "900", "CANCELLED"),
            ("O4", "C1", "2024-04-30", "900", "DELIVERED"),
        ])
        result = aggregate_customer_orders(self.customers, orders).set_index("customer_id")
        self.assertEqual(result.loc["C1", "total_orders"], 2)
        self.assertEqual(result.loc["C1", "total_spent"], 1500.0)
        self.assertEqual(result.loc["C1", "average_order_value"], 750.0)
        self.assertEqual(result.loc["C2", "total_orders"], 0)

    def test_invalid_order_date_ignored(self):
        result = aggregate_customer_orders(self.customers, self.orders([("O1", "C1", "bad-date", "100", "DELIVERED")]))
        self.assertEqual(result["total_orders"].sum(), 0)

    def test_negative_order_amount_ignored(self):
        result = aggregate_customer_orders(self.customers, self.orders([("O1", "C1", "2024-05-01", "-1", "DELIVERED")]))
        self.assertEqual(result["total_spent"].sum(), 0)

    def test_unknown_customer_and_non_numeric_amount_ignored(self):
        orders = self.orders([
            ("O1", "C999", "2024-05-01", "100", "DELIVERED"),
            ("O2", "C1", "2024-05-01", "not-money", "DELIVERED"),
        ])
        with self.assertLogs(level="WARNING") as logs:
            result = aggregate_customer_orders(self.customers, orders)
        self.assertEqual(result["total_orders"].sum(), 0)
        self.assertTrue(any("unknown customer" in line for line in logs.output))

if __name__ == "__main__":
    unittest.main()
