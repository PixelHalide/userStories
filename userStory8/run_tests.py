import ast
import linecache
import sys
import trace
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
TESTS_DIR = PROJECT_ROOT / "tests"
CORE_SOURCE_FILES = {
    "billing_engine.py",
    "status_engine.py",
    "usage_aggregator.py",
}


def main():
    runner = trace.Trace(count=True, trace=False)
    result = runner.runfunc(run_suite)

    coverage_percent = calculate_coverage(runner.results().counts)
    print(f"\nCoverage: {coverage_percent:.2f}%")

    if coverage_percent < 80:
        print("Coverage check failed: minimum required coverage is 80%.")
        sys.exit(1)

    if not result.wasSuccessful():
        sys.exit(1)


def run_suite():
    suite = unittest.defaultTestLoader.discover(str(TESTS_DIR))
    return unittest.TextTestRunner(verbosity=2).run(suite)


def calculate_coverage(line_counts):
    executable_lines = find_executable_lines()
    covered_lines = {
        (Path(file_path).resolve(), line_number)
        for file_path, line_number in line_counts
        if is_core_source_file(file_path)
    }

    if not executable_lines:
        return 100.0

    covered_count = len(executable_lines & covered_lines)
    return (covered_count / len(executable_lines)) * 100


def find_executable_lines():
    executable_lines = set()

    for file_path in SRC_DIR.glob("*.py"):
        if file_path.name not in CORE_SOURCE_FILES:
            continue

        tree = ast.parse(file_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if hasattr(node, "lineno") and is_executable_node(node, file_path):
                executable_lines.add((file_path.resolve(), node.lineno)) # type: ignore

    return executable_lines


def is_core_source_file(file_path):
    path = Path(file_path).resolve()
    return path.parent == SRC_DIR and path.name in CORE_SOURCE_FILES


def is_executable_node(node, file_path):
    if isinstance(node, (ast.Module, ast.Load, ast.Store, ast.Del)):
        return False

    source_line = linecache.getline(str(file_path), node.lineno).strip()
    return bool(source_line) and not source_line.startswith("#")


if __name__ == "__main__":
    main()
