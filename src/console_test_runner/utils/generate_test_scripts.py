import json
import sys
from pathlib import Path
import argparse


class TestScriptGenerator:
    def __init__(self, runspec_file, output_dir):
        self.runspec_file = Path(runspec_file)
        self.output_dir = Path(output_dir)
        self.runspec_data = self.load_runspec()

    def load_runspec(self):
        with open(self.runspec_file, "r") as file:
            return json.load(file)

    def generate_test_scripts(self):
        test_script_template = """
# ################ JAMA SYNC CONFIG START ####################################
# Sync Items: {jama_sync_folder}
# ################ JAMA SYNC CONFIG END ######################################

import pytest
from console_test_runner.test_runner import ConsoleTestRunner

@pytest.fixture(scope="module")
def setup_environment():
    # Set up the environment for tests
    base_path = Path("{base_path}")
    input_folder = Path("{input_folder}")
    output_folder = Path("{output_folder}")
    tool_name = "{tool_name}"
    executable = base_path / tool_name
    return {{
        "executable": executable,
        "input_folder": input_folder,
        "output_folder": output_folder,
    }}

def test_{test_name}(setup_environment):
    \"\"\"
    ################## TEST CASE HEADER V1 START #################################
    Jama ID: {jama_id}
    Jama URL: {jama_url}
    Name: {test_name}
    Version: 1
    ################## TEST CASE HEADER END ######################################
    \"\"\"
    env = setup_environment
    input_file = env["input_folder"] / "{input_file}"
    output_file = env["output_folder"] / "{output_file}"
    arguments = {arguments}
    check_output_exist = {check_output_exist}
    compare_string = {compare_string}

    runner = ConsoleTestRunner(env["executable"])
    test_case = {{
        "name": "{test_name}",
        "inputs": str(input_file),
        "output": str(output_file),
        "arguments": arguments,
        "check_output_exist": check_output_exist,
        "compare_string": compare_string,
    }}
    runner.run_test(test_case)
"""

        for test_case in self.runspec_data["tests"]:
            test_name = test_case["name"]
            jama_id = test_case.get("jama_id", "UNKNOWN")
            jama_url = test_case.get("jama_url", "UNKNOWN")
            input_file = test_case.get("inputs", "")
            output_file = test_case.get("output", "")
            arguments = test_case.get("arguments", [])
            check_output_exist = test_case.get("check_output_exist", False)
            compare_string = test_case.get("compare_string", "")

            test_script = test_script_template.format(
                jama_sync_folder=self.runspec_data["general"].get(
                    "jama_Sync_folder", "UNKNOWN"
                ),
                jama_id=jama_id,
                jama_url=jama_url,
                test_name=test_name,
                base_path=self.runspec_data["general"]["base_path"],
                input_folder=self.runspec_data["general"]["input_folder"],
                output_folder=self.runspec_data["general"]["output_folder"],
                tool_name=self.runspec_data["general"]["tool_name"],
                input_file=input_file,
                output_file=output_file,
                arguments=arguments,
                check_output_exist=check_output_exist,
                compare_string=compare_string,
            )

            test_script_file = self.output_dir / f"test_{test_name}.py"
            with open(test_script_file, "w") as file:
                file.write(test_script)

        print("Test scripts generated successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate test scripts from a runspec file."
    )
    parser.add_argument("runspec_file", help="Path to the runspec file")
    parser.add_argument(
        "output_dir", help="Directory to save the generated test scripts"
    )
    args = parser.parse_args()

    generator = TestScriptGenerator(args.runspec_file, args.output_dir)
    generator.generate_test_scripts()
