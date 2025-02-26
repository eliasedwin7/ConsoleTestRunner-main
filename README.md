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

## 💎 Contact

For any issues, reach out to **Edwin Alias** - edwin.alias@seeingmachines.com.

