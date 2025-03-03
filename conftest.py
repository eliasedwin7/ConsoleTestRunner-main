import pytest
import json
import os


def pytest_addoption(parser):
    """Add a command-line option for specifying the runspec file."""
    parser.addoption(
        "--runspec",
        action="store",
        default=None,
        help="Path to the runspec JSON file",
    )


@pytest.fixture
def runspec_file(request):
    """Fixture to get the runspec file path from the command-line argument."""
    runspec_path = request.config.getoption("--runspec")
    if not runspec_path or not os.path.exists(runspec_path):
        pytest.skip(f"Runspec file '{runspec_path}' not found.")
    return runspec_path


def load_test_cases(runspec_file):
    """Load test cases from the specified runspec file."""
    with open(runspec_file, "r") as file:
        runspec_data = json.load(file)
        return [(test["name"], test) for test in runspec_data["tests"]]


def pytest_generate_tests(metafunc):
    """Dynamically parametrize tests based on the provided runspec file."""
    if "test_name" in metafunc.fixturenames and "test_case" in metafunc.fixturenames:
        runspec_file = metafunc.config.getoption("--runspec")
        if runspec_file and os.path.exists(runspec_file):
            test_cases = load_test_cases(runspec_file)
            metafunc.parametrize(
                "test_name, test_case", test_cases, ids=[t[0] for t in test_cases]
            )
