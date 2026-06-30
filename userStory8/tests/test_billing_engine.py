import unittest

from userStory8.src.billing_engine import calculate_bill


class TestBillingEngine(unittest.TestCase):
    def test_bill_without_overage(self):
        overage_gb, total_bill = calculate_bill(499, 50, 40, "ACTIVE")

        self.assertEqual(overage_gb, 0)
        self.assertEqual(total_bill, 499)

    def test_bill_with_overage(self):
        overage_gb, total_bill = calculate_bill(499, 50, 60, "ACTIVE")

        self.assertEqual(overage_gb, 10)
        self.assertEqual(total_bill, 599)

    def test_suspended_subscription_billing(self):
        overage_gb, total_bill = calculate_bill(999, 200, 230, "SUSPENDED")

        self.assertEqual(overage_gb, 30)
        self.assertEqual(total_bill, 999)

    def test_cancelled_subscription_billing(self):
        overage_gb, total_bill = calculate_bill(1999, 500, 600, "CANCELLED")

        self.assertEqual(overage_gb, 0)
        self.assertEqual(total_bill, 0)


if __name__ == "__main__":
    unittest.main()
