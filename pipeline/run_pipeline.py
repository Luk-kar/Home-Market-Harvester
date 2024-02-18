"""
This script orchestrates the execution of a data processing pipeline, ensuring that
environment settings are initialized, essential environment variables are validated,
and various stages of the pipeline (such as data scraping, cleaning, model training,
and data visualization) are executed in a specific order.

The pipeline leverages external scripts and tools, managing execution through subprocess
calls and handling errors and exit codes appropriately to ensure robust execution.
Environment settings are managed via a .env file, which is validated at runtime to
ensure all required configurations are set.

Usage:
    Run this script directly from the command line to execute the entire pipeline.
    Ensure the .env file is properly configured in the script's directory before running.

Features:
- Initializes environment settings from a .env file.
- Validates essential environment variables for the pipeline's operation.
- Executes pipeline stages defined as external scripts or Jupyter notebooks.
- Handles subprocess execution, including error handling and exit code management.
- Logs execution details and prints status updates to the console.

Requirements:
- A .env file with the necessary environment variables must be present in the same
  directory as this script.

WARNING:
The order of function invocations within the script is critical to its correct operation.
"""

# Standard library imports
import argparse
import sys
from pathlib import Path

# Third-party imports
from dotenv import load_dotenv


def set_sys_path_to_project_root(__file__: str):
    """
    Adds the project root to the system path.

    Args:
        __file__ (str): The path to the current file.
    """
    root_dir = Path(__file__).resolve().parents[1]
    sys.path.append(str(root_dir))


set_sys_path_to_project_root(__file__)

# Local imports
from pipeline.components.environment import (
    initialize_environment_settings,
    set_user_data_path_env_var,
)
from pipeline.components.logging import setup_logging
from pipeline.components.pipeline_flow import run_pipeline


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for the pipeline.

    Returns:
        argparse.Namespace: The parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Run the data processing pipeline.")

    default_args = {
        "location_query": 1500,
        "area_radius": 25,
        "scraped_offers_cap": 100,
    }

    parser.add_argument(
        "--location_query",
        type=str,
        default=default_args["location_query"],
        help=f"The location query for scraping. Defaults to '{default_args['location_query']}'.",
    )
    parser.add_argument(
        "--area_radius",
        type=int,
        default=default_args["area_radius"],
        help=(
            "The radius of the area for scraping in kilometers."
            f"Defaults to {default_args['area_radius']}."
        ),
    )

    parser.add_argument(
        "--scraped_offers_cap",
        type=int,
        default=default_args["scraped_offers_cap"],
        help=(
            "The maximum number of offers to scrape."
            f"Defaults to {default_args['scraped_offers_cap']}."
        ),
    )
    parser.add_argument(
        "--user_data_path",
        type=str,
        nargs="?",
        help="The path to the user data file in CSV format to display in the dashboard.",
    )

    command_arguments = parser.parse_args()
    return command_arguments


if __name__ == "__main__":

    initialize_environment_settings()

    setup_logging()

    command_args = parse_arguments()

    environment_path = Path(".env")
    if command_args.user_data_path:
        set_user_data_path_env_var(command_args, environment_path, "USER_OFFERS_PATH")

    load_dotenv(dotenv_path=environment_path)  # Load environment variables from .env

    stages = [
        str(Path("pipeline") / "stages" / "a_scraping"),
        str(Path("pipeline") / "stages" / "b_cleaning" / "a_cleaning_OLX.ipynb"),
        str(Path("pipeline") / "stages" / "b_cleaning" / "b_cleaning_otodom.ipynb"),
        str(Path("pipeline") / "stages" / "b_cleaning" / "c_combining_data.ipynb"),
        str(Path("pipeline") / "stages" / "b_cleaning" / "d_creating_map_data.py"),
        str(Path("pipeline") / "stages" / "c_model_developing" / "model_training.py"),
        str(Path("pipeline") / "stages" / "d_data_visualizing" / "streamlit_app.py"),
    ]

    run_pipeline(stages, command_args)
