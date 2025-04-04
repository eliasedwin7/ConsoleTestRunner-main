import platform
from pathlib import Path
from inspect import currentframe
from os import environ
import re


class SMHelper:
    """Utility class for SM-specific functions."""

    @staticmethod
    def resolve_paths(parameters: dict) -> Path:
        """Check the existence of input and output folders, and get their full path.
        Then it creates the output directory.

        Args:
            parameters (dict): Dictionary of test parameters.
                needed parameters keys:
                    input_local_dir_bool, input_folder_dir

        Returns:
            Path: The resolved input directory path.
        """
        test_input = ""
        if not parameters["input_local_dir_bool"]:
            if "EOD_BASE" in environ:
                test_input = Path(environ["EOD_BASE"]) / parameters["input_folder_dir"]
            elif platform.system() == "Linux":
                test_input = (
                    Path("/mnt/public/FLIB/EOD_WIP/oms001/Test/OMS_Test_Data")
                    / parameters["input_folder_dir"]
                )
            elif platform.system() == "Windows":
                test_input = (
                    Path(r"P:\\FLIB\\EOD_WIP\\oms001\\Test\\OMS_Test_Data")
                    / parameters["input_folder_dir"]
                )
        else:
            test_input = Path.cwd() / parameters["input_folder_dir"]

        if test_input.exists():
            return test_input
        else:
            error_reason = (
                f"Input directory issue: This directory {test_input} does not exist"
            )
            func_name = currentframe().f_code.co_name
            raise RuntimeError(f"\nError in {func_name} function.\n{error_reason}")

    @staticmethod
    def find_xplat_root() -> Path:
        """Finds the root directory containing 'xplat' by traversing upwards."""
        script_dir = Path(__file__).resolve().parent
        root_folder = script_dir

        while root_folder.name != "xplat" and root_folder.parent != root_folder:
            root_folder = root_folder.parent

        if root_folder.name != "xplat":
            raise RuntimeError(
                "Could not find 'xplat' directory in the path hierarchy."
            )

        return root_folder


    @staticmethod
    def resolve_keywords(value):
        """Recursively resolve {ROOT}, {RESOLVE_BASE}, and {_FILE_} keywords in config values."""
        if isinstance(value, str):
            root_path = str(SMHelper.find_xplat_root()).replace("\\", "\\\\") 
            base_path = str(SMHelper.resolve_paths(
                {"input_local_dir_bool": False, "input_folder_dir": ""}
            )).replace("\\", "\\\\") 
            file_path = str(Path(__file__).resolve().parent).replace("\\", "\\\\")  

            value = re.sub(r"\{ROOT\}", root_path, value)
            value = re.sub(r"\{RESOLVE_BASE\}", base_path, value)
            value = re.sub(r"\{_FILE_\}", file_path, value)

        elif isinstance(value, dict):
            return {key: SMHelper.resolve_keywords(val) for key, val in value.items()}
        
        elif isinstance(value, list):
            return [SMHelper.resolve_keywords(item) for item in value]

        return value