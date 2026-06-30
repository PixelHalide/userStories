import unittest

from userStory8.src.status_engine import evaluate_status


class TestStatusEngine(unittest.TestCase):
    def test_active_to_suspended_transition(self):
        final_status = evaluate_status("ACTIVE", 80, 50)

        self.assertEqual(final_status, "SUSPENDED")

    def test_suspended_to_active_transition(self):
        final_status = evaluate_status("SUSPENDED", 45, 50)

        self.assertEqual(final_status, "ACTIVE")

    def test_cancelled_status_unchanged(self):
        final_status = evaluate_status("CANCELLED", 1000, 50)

        self.assertEqual(final_status, "CANCELLED")


if __name__ == "__main__":
    unittest.main()
