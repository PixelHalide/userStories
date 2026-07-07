import os
import unittest
from pathlib import Path

import coverage


ROOT = Path(__file__).resolve().parent


def main() -> int:
    os.chdir(ROOT)
    cov = coverage.Coverage(include=["src/sales_aggregator.py", "src/inventory_engine.py"])
    cov.start()

    suite = unittest.defaultTestLoader.discover("tests")
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    cov.stop()
    cov.save()

    print()
    cov.report(show_missing=True)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
