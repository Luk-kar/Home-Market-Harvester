"""
This module serves as the orchestrator for a comprehensive data processing pipeline. 
It is designed to systematically execute various stages of the pipeline, 
including data scraping, cleaning, model training, and data visualization, in a predetermined sequence. 
The orchestration process involves initializing environment settings, validating essential environment variables, 
and managing the execution of external scripts or Jupyter notebooks through subprocess calls. 
This approach ensures robust execution by handling errors and exit codes effectively.

Key functionalities include:
- Environment setup from a .env file, ensuring all necessary configurations are present 
  and correct for the pipeline's operation.
- Validation of essential environment variables at runtime to avoid configuration errors.
- Modular execution of pipeline stages, allowing for flexibility in processing different types of tasks 
  (e.g., Python scripts, Jupyter notebooks).
- Comprehensive logging of execution details and status updates, 
  facilitating monitoring and debugging of the pipeline process.

Usage:
    The module can be executed directly from the command line. 
    Before running, ensure that the .env file is correctly set up 
    in the project's root directory to configure the pipeline environment properly.

Requirements:
- Presence of a .env file in the same directory as root project, 
  containing all required environment variables.

WARNING:
The order in which functions are invoked is crucial for the correct operation of the script. 
Adjustments to the execution sequence should be made 
with an understanding of the pipeline's architecture and dependencies.

Example Command:
    python run_pipeline.py --location_query "Warszawa" --area_radius 50 --scraped_offers_cap 500 --user_data_path "/path/to/user/data.csv"
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
