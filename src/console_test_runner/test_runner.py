import logging
import json
import pytest
from pathlib import Path
from console_test_runner.utils.helper import ConsoleTestUtils

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ConsoleTestRunner:
    """Console Test Runner class for executing tests based on configuration."""

    def __init__(self, runspec_file: str):
        self.runspec_file = Path(runspec_file)
        assert self.runspec_file.exists(), f"Runspec file {self.runspec_file} not found"
        self.test_config = self.load_config()
        self.environment = self.setup_environment()

    def load_config(self):
        """Loads the test configuration from the runspec JSON file."""
        logging.info(f"Loading configuration from {self.runspec_file}")
        with self.runspec_file.open("r") as f:
            return json.load(f)

    def setup_environment(self):
        """Sets up the test environment based on JSON configuration."""
        config = self.test_config["general"]
        base_path = Path(config["base_path"]).resolve()
        input_dir = base_path / config["input_folder"]
        output_dir = base_path / config["output_folder"]
        ConsoleTestUtils.ensure_directory_exists(output_dir)

        executable_name = config["tool_name"]
        tool_path = ConsoleTestUtils.get_executable(
            base_path, base_path / "extracted", executable_name
        )
        logging.info(f"Executable found at {tool_path}")
        return {
            "executable": tool_path,
            "output_dir": output_dir,
            "base_path": base_path,
            "input_dir": input_dir,
        }

    def run_test(self, test_case):
        """Executes and validates a single test case."""
        logging.info(f"Running test: {test_case['name']}")

        inputs = test_case.get("inputs", [])
        outputs = test_case.get("output", [])
        if isinstance(inputs, str):
            inputs = [inputs]
        if isinstance(outputs, str):
            outputs = [outputs]

        input_files = [
            (
                Path(inp).resolve()
                if Path(inp).is_absolute()
                else self.environment["input_dir"] / inp
            )
            for inp in inputs
            if inp
        ]
        for inp in input_files:
            ConsoleTestUtils.check_file_exists(inp)

        output_files = [
            (
                Path(out).resolve()
                if Path(out).is_absolute()
                else self.environment["output_dir"] / out
            )
            for out in outputs
            if out
        ]
        tool_args = [
            (
                arg.replace("{INPUT}", str(input_files[idx].parent))
                if "{INPUT}" in arg
                else arg
            )
            for idx, arg in enumerate(test_case["arguments"])
        ]

        input_args = " ".join(str(inp) for inp in input_files)
        output_args = " ".join(str(out) for out in output_files)

        if input_files and output_files:
            ConsoleTestUtils.run_conversion(
                str(self.environment["executable"]),
                "--input",
                input_args,
                "--output",
                output_args,
                *tool_args,
            )

        check_output_exist = test_case.get("check_output_exist", True)
        if check_output_exist:
            for output_file in output_files:
                assert output_file.exists(), f"Output file {output_file} does not exist"
        if "compare_string" in test_case:
            ConsoleTestUtils.compare_argument(
                str(self.environment["executable"]), test_case["compare_string"]
            )
        logging.info(f"Test passed: {test_case['name']}")

    def run_all_tests(self):
        """Runs all test cases defined in the runspec file."""
        logging.info("Starting all tests")
        for test_case in self.test_config["tests"]:
            self.run_test(test_case)
        logging.info("All tests completed successfully")
