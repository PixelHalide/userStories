import unittest

import pandas as pd

from src.sales_aggregator import aggregate_april_sales


class SalesAggregationTests(unittest.TestCase):
    def setUp(self):
        self.inventory = pd.DataFrame(
            [
                {"product_id": "P001", "product_name": "Laptop", "current_stock": 10, "unit_price": 100, "category": "Electronics"},
                {"product_id": "P002", "product_name": "Mouse", "current_stock": 5, "unit_price": 20, "category": "Accessories"},
            ]
        )

    def test_multiple_sales_aggregation(self):
        sales = pd.DataFrame(
            [
                {"transaction_id": "T1", "product_id": "P001", "transaction_date": "2024-04-01", "quantity_sold": 2},
                {"transaction_id": "T2", "product_id": "P001", "transaction_date": "2024-04-02", "quantity_sold": 3},
                {"transaction_id": "T3", "product_id": "P002", "transaction_date": "2024-04-03", "quantity_sold": 1},
            ]
        )
        result, processed = aggregate_april_sales(sales, self.inventory)
        totals = dict(zip(result["product_id"], result["total_sold_quantity"]))

        self.assertEqual(totals["P001"], 5)
        self.assertEqual(totals["P002"], 1)
        self.assertEqual(processed, 3)

    def test_invalid_transaction_date(self):
        sales = pd.DataFrame(
            [
                {"transaction_id": "T1", "product_id": "P001", "transaction_date": "bad-date", "quantity_sold": 2},
                {"transaction_id": "T2", "product_id": "P001", "transaction_date": "2024-04-02", "quantity_sold": 3},
            ]
        )
        result, processed = aggregate_april_sales(sales, self.inventory)

        self.assertEqual(result.loc[0, "total_sold_quantity"], 3)
        self.assertEqual(processed, 1)

    def test_negative_quantity_ignored(self):
        sales = pd.DataFrame(
            [
                {"transaction_id": "T1", "product_id": "P001", "transaction_date": "2024-04-01", "quantity_sold": -2},
                {"transaction_id": "T2", "product_id": "P001", "transaction_date": "2024-04-02", "quantity_sold": 3},
            ]
        )
        result, processed = aggregate_april_sales(sales, self.inventory)

        self.assertEqual(result.loc[0, "total_sold_quantity"], 3)
        self.assertEqual(processed, 1)


if __name__ == "__main__":
    unittest.main()
