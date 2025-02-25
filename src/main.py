import argparse
import logging
from test_runner import ConsoleTestRunner

# Configure logging to print to console
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Console Test Runner")
    parser.add_argument("--runspec", required=True, help="Path to the runspec JSON file")
    args = parser.parse_args()

    logging.info("Starting Console Test Runner")
    runner = ConsoleTestRunner(args.runspec)
    runner.run_all_tests()
    
    logging.info("Test execution completed")
