import unittest

import pandas as pd

from src.inventory_engine import get_stock_status, reconcile_inventory


class InventoryCalculationTests(unittest.TestCase):
    def test_inventory_reduction(self):
        inventory = pd.DataFrame(
            [{"product_id": "P001", "product_name": "Laptop", "current_stock": 10, "unit_price": 100, "category": "Electronics"}]
        )
        sales = pd.DataFrame([{"product_id": "P001", "total_sold_quantity": 4}])

        result = reconcile_inventory(inventory, sales)

        self.assertEqual(result.loc[0, "final_stock"], 6)
        self.assertEqual(result.loc[0, "total_sales_value"], 400)

    def test_inventory_not_negative(self):
        inventory = pd.DataFrame(
            [{"product_id": "P001", "product_name": "Laptop", "current_stock": 3, "unit_price": 100, "category": "Electronics"}]
        )
        sales = pd.DataFrame([{"product_id": "P001", "total_sold_quantity": 5}])

        result = reconcile_inventory(inventory, sales)

        self.assertEqual(result.loc[0, "final_stock"], 0)
        self.assertEqual(result.loc[0, "stock_status"], "OUT_OF_STOCK")

    def test_zero_stock_status(self):
        inventory = pd.DataFrame(
            [{"product_id": "P001", "product_name": "Laptop", "current_stock": 4, "unit_price": 100, "category": "Electronics"}]
        )
        sales = pd.DataFrame([{"product_id": "P001", "total_sold_quantity": 4}])

        result = reconcile_inventory(inventory, sales)

        self.assertEqual(result.loc[0, "stock_status"], "OUT_OF_STOCK")


class StockStatusTests(unittest.TestCase):
    def test_available_status(self):
        self.assertEqual(get_stock_status(11), "AVAILABLE")

    def test_low_stock_status(self):
        self.assertEqual(get_stock_status(10), "LOW_STOCK")
        self.assertEqual(get_stock_status(1), "LOW_STOCK")

    def test_out_of_stock_status(self):
        self.assertEqual(get_stock_status(0), "OUT_OF_STOCK")


if __name__ == "__main__":
    unittest.main()
