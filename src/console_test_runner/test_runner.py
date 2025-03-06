import logging
import json
import pytest
from pathlib import Path
from console_test_runner.utils.sm_helper import SMHelper
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
        tool_path = config["tool_path"]
        input_dir = config["input_folder"]
        output_dir = config["output_folder"]

        if "{ROOT}" in tool_path:
            root_path = SMHelper.find_xplat_root()
            tool_path = tool_path.replace("{ROOT}", str(root_path))
        if "{RESOLVE_BASE}" in input_dir:
            base_path = SMHelper.resolve_paths(
                {
                    "input_local_dir_bool": False,
                    "input_folder_dir": config["input_folder"],
                }
            )
            input_dir = input_dir.replace("{RESOLVE_BASE}", str(base_path))
        if "{RESOLVE_BASE}" in output_dir:
            base_path = SMHelper.resolve_paths(
                {
                    "input_local_dir_bool": False,
                    "input_folder_dir": config["input_folder"],
                }
            )
            output_dir = output_dir.replace("{RESOLVE_BASE}", str(base_path))

        tool_path = Path(tool_path).resolve()
        input_dir = Path(input_dir).resolve()
        output_dir = Path(output_dir).resolve()
        ConsoleTestUtils.ensure_directory_exists(output_dir)

        executable_name = config["tool_name"]
        tool_path = ConsoleTestUtils.get_executable(
            tool_path, tool_path, executable_name
        )
        logging.info(f"Executable found at {tool_path}")

        environment = {
            "executable": tool_path,
            "output_dir": output_dir,
            "input_dir": input_dir,
        }

        if "license_key" in config:
            environment["license_key"] = Path(config["license_key"]).resolve()

        return environment
        if "license_key" in config:
            environment["license_key"] = Path(config["license_key"]).resolve()

        return environment

    def run_test(self, test_case):
        """Executes and validates a single test case."""
        logging.info(f"Running test: {test_case['name']}")
        expect_error = test_case.get("expect_error", False)
        dettach_license = test_case.get("dettach_license", False)
        cleanup = self.test_config["general"].get("cleanup", False)
        license_backup = None
        output_files = []

        try:
            if dettach_license and "license_key" in self.environment:
                license_backup = self.environment["license_key"].with_suffix(".bak")
                self.environment["license_key"].rename(license_backup)
                logging.info(f"License key renamed to {license_backup}")

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

            # Check the flag to determine whether to create the output directory
            create_output_dir = test_case.get("create_output_dir", True)
            if create_output_dir:
                for output_file in output_files:
                    output_file.parent.mkdir(parents=True, exist_ok=True)

            # Use the parent directory of the first input file if available, otherwise use the input directory
            input_dir = (
                str(input_files[0].parent)
                if input_files
                else str(self.environment["input_dir"])
            )

            tool_args = [
                arg.replace("{INPUT}", input_dir) if "{INPUT}" in arg else arg
                for arg in test_case.get("arguments", [])
            ]

            if (
                (not inputs or all(not inp for inp in inputs))
                and (not outputs or all(not out for out in outputs))
                and (not tool_args or all(not arg for arg in tool_args))
            ):
                raise ValueError(
                    "Inputs, outputs, and arguments are all empty. At least one must be provided."
                )

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
                    assert (
                        output_file.exists()
                    ), f"Output file {output_file} does not exist"
            if "compare_string" in test_case:
                ConsoleTestUtils.compare_argument(
                    str(self.environment["executable"]), test_case["compare_string"]
                )
            if expect_error:
                raise AssertionError("Expected an error but the test passed.")
            logging.info(f"Test passed: {test_case['name']}")
        except (RuntimeError, FileNotFoundError, ValueError) as e:
            if not expect_error:
                raise e
            logging.info(f"Test failed as expected: {test_case['name']} - {e}")
        finally:
            if dettach_license and license_backup:
                license_backup.rename(self.environment["license_key"])
                logging.info(f"License key restored from {license_backup}")
            if cleanup:
                for output_file in output_files:
                    if output_file.exists():
                        output_file.unlink()
                        logging.info(f"Deleted output file: {output_file}")

    def run_all_tests(self):
        """Runs all test cases defined in the runspec file."""
        logging.info("Starting all tests")
        for test_case in self.test_config["tests"]:
            self.run_test(test_case)
        logging.info("All tests completed successfully")
