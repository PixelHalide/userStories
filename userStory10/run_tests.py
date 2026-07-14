"""Run unit tests and print coverage for core modules."""
import sys
import unittest
from coverage import Coverage

coverage = Coverage(source=["src"], omit=["src/main.py"])
coverage.start()
suite = unittest.defaultTestLoader.discover("tests")
result = unittest.TextTestRunner(verbosity=2).run(suite)
coverage.stop()
coverage.save()
percent = coverage.report(show_missing=True)
sys.exit(0 if result.wasSuccessful() and percent >= 80 else 1)
