import subprocess
import threading
import tarfile
import zipfile
import logging
from pathlib import Path
import glob
import shutil
import platform
from os import environ, getcwd
from typing import List, Optional, Union
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class AuthorizationError(Exception):
    """Exception raised for authorization errors."""

    pass


class ConsoleTestUtils:
    """Utility class for Console Test Runner"""

    @staticmethod
    def extract_package(package_path: Path, extract_to: Path) -> None:
        """Extracts the package if it is a zip or tar file."""
        logging.info(f"Extracting package {package_path} to {extract_to}")
        if package_path.suffix == ".zip":
            with zipfile.ZipFile(package_path, "r") as zip_ref:
                zip_ref.extractall(extract_to)
        elif package_path.suffix in [".tar", ".gz"]:
            with tarfile.open(package_path, "r:*") as tar_ref:
                tar_ref.extractall(extract_to)
        else:
            logging.error("Unsupported package format")
            raise ValueError("Unsupported package format")

    @staticmethod
    def find_executable(main_folder: Path, executable_name: str) -> Path:
        """Finds the executable within the specified folder."""
        logging.info(f"Searching for executable {executable_name} in {main_folder}")
        for p in main_folder.rglob("*"):
            if p.name == executable_name and p.is_file():
                logging.info(f"Found executable: {p}")
                return p
        logging.error(f"Executable {executable_name} not found in {main_folder}")
        raise FileNotFoundError(f"{executable_name} not found in {main_folder}")

    @staticmethod
    def ensure_directory_exists(directory: Path) -> None:
        """Ensures that the specified directory exists."""
        logging.info(f"Ensuring directory exists: {directory}")
        directory.mkdir(parents=True, exist_ok=True)
        if platform.system() != "Windows":
            os.chmod(directory, 0o755)

    @staticmethod
    def run_conversion(*args: str) -> str:
        """Runs the conversion command and returns the output.

        Args:
            *args (str): The command arguments.

        Returns:
            str: The command output.

        Raises:
            AuthorizationError: If authorization fails.
            RuntimeError: If the conversion fails.
        """
        print(f"\nRunning command: {' '.join(args)}")

        def monitor_stdout(
            proc: subprocess.Popen,
            stop_event: threading.Event,
            exception_container: List[Exception],
        ) -> None:
            try:
                for line in iter(proc.stdout.readline, ""):
                    if (
                        "INTERNAL SM_EXCEPTION:" in line
                        or "ERROR" in line
                        or "Error" in line
                    ):
                        print(f"Detected error in output: {line.strip()}")
                        if (
                            "Failed to authorize" in line
                            or " Authentication failed" in line
                        ):
                            stop_event.set()
                            proc.terminate()
                            raise AuthorizationError(line.strip())
                        stop_event.set()
                        proc.terminate()
                        break
                    print(line, end="")
            except Exception as e:
                exception_container.append(e)
                stop_event.set()
                proc.terminate()

        try:
            proc = subprocess.Popen(
                args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            stop_event = threading.Event()
            exception_container: List[Exception] = []
            monitor_thread = threading.Thread(
                target=monitor_stdout, args=(proc, stop_event, exception_container)
            )
            monitor_thread.start()
            monitor_thread.join()
            stdout, stderr = proc.communicate()
            if exception_container:
                raise exception_container[0]
            if proc.returncode != 0 or stop_event.is_set():
                raise subprocess.CalledProcessError(
                    proc.returncode, args, output=stdout, stderr=stderr
                )
            return stdout
        except subprocess.CalledProcessError as e:
            e_error = e.stderr if e.stderr else e.output
            raise RuntimeError(f"Conversion failed: {e_error}")

    @staticmethod
    def get_executable(
        main_folder: Path, extract_to: Path, executable_name: str
    ) -> Path:
        """Gets the executable, extracting it if necessary."""
        logging.info(f"Retrieving executable: {executable_name}")
        try:
            return ConsoleTestUtils.find_executable(main_folder, executable_name)
        except FileNotFoundError:
            zip_files = glob.glob(
                f"**/zip/{executable_name.split('.')[0]}*.zip", recursive=True
            )
            if not zip_files:
                logging.error("No executable or package found.")
                raise FileNotFoundError("No executable or package found.")
            logging.info(f"Extracting from package: {zip_files[0]}")
            ConsoleTestUtils.extract_package(Path(zip_files[0]), extract_to)
        return ConsoleTestUtils.find_executable(extract_to, executable_name)

    # TODO: Add the compare_argument method to the ConsoleTestUtils class.
    @staticmethod
    def compare_argument(executable: str, help_argument: str):
        """Compares the help argument with the actual output."""
        result = subprocess.run([executable, "--help"], capture_output=True, text=True)
        actual_output = result.stdout
        # Normalize whitespace and compare
        actual_normalized = " ".join(actual_output.split())
        expected_normalized = " ".join(help_argument.split())

        assert (
            expected_normalized in actual_normalized
        ), f"Mismatch: {actual_normalized} != {expected_normalized}"

    @staticmethod
    def delete_generated_packages(
        option: bool, directories: Union[List[Path], Path]
    ) -> None:
        """Deletes the specified directories if option is enabled."""
        if option:
            logging.info(f"Deleting generated packages: {directories}")
            if isinstance(directories, list):
                for directory in directories:
                    if directory.exists() and directory.is_dir():
                        shutil.rmtree(directory)
            else:
                if directories.exists() and directories.is_dir():
                    shutil.rmtree(directories)

    @staticmethod
    def read_runspec_file(runspec_file: Path) -> Optional[List[dict]]:
        """Reads a runspec JSON file."""
        logging.info(f"Reading configuration file: {runspec_file}")
        try:
            with runspec_file.open("r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON format in {runspec_file}: {e}")
            raise ValueError(f"Invalid JSON format: {e}")

    @staticmethod
    def check_file_exists(file_path: Path) -> None:
        """Check if a file exists and raise an error if not."""
        logging.info(f"Checking if file exists: {file_path}")
        if not file_path.exists():
            logging.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
