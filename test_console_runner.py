import pytest
from console_test_runner.test_runner import ConsoleTestRunner


def test_console_runner(test_name, test_case, runspec_file):
    """Runs each test case separately from the runspec file."""
    runner = ConsoleTestRunner(runspec_file)
    print(f"\nRunning test: {test_name} from {runspec_file}")
    runner.run_test(test_case)
