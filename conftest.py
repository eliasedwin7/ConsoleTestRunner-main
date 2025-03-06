import pytest
from pathlib import Path
from console_test_runner.utils.helper import ConsoleTestUtils


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
    runspec_path = Path(request.config.getoption("--runspec"))
    if not runspec_path or not ConsoleTestUtils.check_file_exists(runspec_path):
        pytest.skip(f"Runspec file '{runspec_path}' not found.")
    return runspec_path


def load_test_cases(runspec_file):
    """Load test cases from the specified runspec file."""
    runspec_data = ConsoleTestUtils.read_runspec_file(runspec_file)
    return [(test["name"], test) for test in runspec_data["tests"]]


def pytest_generate_tests(metafunc):
    """Dynamically parametrize tests based on the provided runspec file."""
    if "test_name" in metafunc.fixturenames and "test_case" in metafunc.fixturenames:
        runspec_file = Path(metafunc.config.getoption("--runspec"))
        if runspec_file and ConsoleTestUtils.check_file_exists(runspec_file):
            test_cases = load_test_cases(runspec_file)
            metafunc.parametrize(
                "test_name, test_case", test_cases, ids=[t[0] for t in test_cases]
            )
