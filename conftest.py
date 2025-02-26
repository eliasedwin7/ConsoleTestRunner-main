import pytest

def pytest_addoption(parser):
    parser.addoption("--runspec", action="store", default=None, help="Path to runspec JSON")

@pytest.fixture
def runspec_file(request):
    return request.config.getoption("--runspec")
