import pytest
import json
from console_test_runner.test_runner import ConsoleTestRunner

# Load test cases from the runspec JSON
with open("inputs/configurations.runspec.json", "r") as file:
    runspec_data = json.load(file)

# Extract test cases and names
test_cases = [(test["name"], test) for test in runspec_data["tests"]]

@pytest.mark.parametrize("test_name, test_case", test_cases, ids=[t[0] for t in test_cases])
def test_console_runner(test_name, test_case):
    """Runs each test case separately from the runspec file, displaying the test name."""
    runspec_file = "inputs/configurations.runspec.json"
    runner = ConsoleTestRunner(runspec_file)

    # Log test execution
    print(f"\nRunning test: {test_name}")

    # Run the specific test case
    runner.run_test(test_case)
