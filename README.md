# Console Test Runner

A command-line test runner that executes tests based on a configuration file (`runspec.json`).

## 📂 Project Structure

```
ConsoleTestRunner-main/
├── src/
│   ├── console_test_runner/
│   │   ├── __init__.py
│   │   ├── test_runner.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── helper.py
│── inputs/
│   ├── configurations.runspec.json
│── test_console_runner.py
│── README.md
│── setup.py / setup.cfg
```

## 🔧 Setup

1. Clone the repository:
   ```sh
   git clone <repository-url>
   cd ConsoleTestRunner-main
   ```
2. Install dependencies:
   ```sh
   pip install -e .
   ```

## 🚀 Running the Application

To run the main application:
```sh
python .\src\main.py --runspec inputs\configurations.runspec.json
```

To run tests:
```sh
pytest .\test_console_runner.py --runspec=.\inputs\configurations.runspec.json -v
```

## 🛠️ Creating the JSON Configuration File
The JSON configuration file (`runspec.json`) defines the tests to be executed. Here is an example of how to create a JSON configuration file:

```json
{
    "general": {
        "base_path": "./inputs",
        "input_folder": "./inputs",
        "output_folder": "./inputs",
        "tool_name": "icms_eod_to_csv.exe",
        "cleanup": true,
        "jama_Sync_folder": "OMS001-FLD-261",
        "license_key": "C:\\Users\\Edwin.Alias\\Documents\\Seeing Machines\\Keys\\keyfile"
    },
    "tests": [
        {
            "name": "test_help_argument",
            "inputs": "",
            "output": "",
            "arguments": ["--help"],
            "check_output_exist": false,
            "compare_string": "Allowed options:\n  -h [ --help ]          Shows this message\n  -i [ --input ] arg     Specify the input filename.\n  -o [ --output ] arg    Specify the output filename, needs to have the extension \".csv\"\n  -f [ --force ]         Will not prompt overwriting of files.\n  -t [ --types ]         Adds a row under keys with the value types.\n  -w [ --whitelist ] arg CSV file containing columns to include in output CSV.\n                         Format is as described above or as generated with\n                         --gen-whitelist.\n  --gen-whitelist        Will generate a default CSV whitelist that enables\n                         every column, which can be used with the --whitelist option.\n  --hide-progress        Will disable progress (useful for old, non-indexed files)",
            "jama_id": "OMS001-SWQTS-1330",
            "jama_url": "https://seeingmachines.jamacloud.com/perspective.req#/testCases/3557552?projectId=181"
        },
        {
            "name": "test_basic_conversion_input",
            "inputs": "test.eod",
            "output": "outputs/result_basic.csv",
            "arguments": ["--force"],
            "check_output_exist": true,
            "jama_id": "OMS001-SWQTS-1331",
            "jama_url": "https://seeingmachines.jamacloud.com/perspective.req#/testCases/3557553?projectId=181"
        },
        {
            "name": "test_all_args_conversion_output",
            "inputs": "test.eod",
            "output": "outputs/result_all_args.csv",
            "arguments": ["--force", "--types", "--whitelist", "{INPUT}//whitelist.csv"],
            "check_output_exist": true,
            "jama_id": "OMS001-SWQTS-1332",
            "jama_url": "https://seeingmachines.jamacloud.com/perspective.req#/testCases/3557554?projectId=181"
        },
        {
            "name": "test_all_args_conversion_force",
            "inputs": "test.eod",
            "output": "outputs/result_all_args.csv",
            "arguments": ["--force", "--types", "--whitelist", "{INPUT}//whitelist.csv"],
            "check_output_exist": true,
            "jama_id": "OMS001-SWQTS-1333",
            "jama_url": "https://seeingmachines.jamacloud.com/perspective.req#/testCases/3557555?projectId=181"
        },
        {
            "name": "test_usecase_invalid_license",
            "inputs": "test.eod",
            "output": "outputs/output_invalid_input.csv",
            "arguments": ["--force"],
            "expect_error": true,
            "jama_id": "OMS001-SWQTS-1392",
            "jama_url": "https://seeingmachines.jamacloud.com/perspective.req#/testCases/4319718?projectId=181",
            "dettach_license": true
        }
    ]
}
```


## 💎 Contact

For any issues, reach out to **Edwin Alias** - edwin.alias@seeingmachines.com.

