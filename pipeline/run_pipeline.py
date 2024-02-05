# Standard imports
from dotenv import load_dotenv
from pathlib import Path
from subprocess import run, CalledProcessError
from typing import Optional
from datetime import datetime
import logging
import os
import re
import sys


def set_sys_path_to_project_root(__file__: str):
    """
    Adds the project root to the system path.

    Args:
        __file__ (str): The path to the current file.
    """
    root_dir = Path(__file__).resolve().parent
    sys.path.append(str(root_dir))


set_sys_path_to_project_root(__file__)


def initialize_environment_settings():
    """
    Creates or verifies an .env file
    with predefined (dummy) environment variables
    for project configuration.

    Raises:
        ValueError: If the .env file is not found or is empty.
    """

    env_path = Path(".env")  # Assuming the root of the project is the project directory
    encoding = "utf-8"

    env_content = (
        # A structure example
        f"USER_OFFERS_PATH={os.path.join('data', 'test', 'your_offers.csv')}\n"
        "MARKET_OFFERS_TIMEPLACE=\n"  # To be created after the scraping stage
        "MODEL_PATH=model.pkl\n"  # To be created after model training
        "LOCATION_QUERY=Warszawa\n"  # Be sure that location fits the query
        "AREA_RADIUS=25\n"  # 0, 5, 10, 15, 25, 50, 75
        "SCRAPED_OFFERS_CAP=5\n"  # Sky is the limit
        "CHROME_DRIVER_PATH=\n"  # path to the ChromeDriver
        "CHROME_BROWSER_PATH=\n"  # path to the Chrome browser
    )

    if not env_path.exists():
        with open(env_path, "w", encoding=encoding) as f:
            f.write(env_content)

    if env_path.read_text(encoding=encoding) == env_content:
        raise ValueError(
            "Please fill in the .env file with your data.\n"
            f"The file {env_path} is located at the root of the project.\n"
            "Reload the environment settings."
        )


initialize_environment_settings()

logging.basicConfig(
    filename=os.path.join("logs", "pipeline.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
)


def run_command(command: list[str], env_vars: Optional[dict] = None) -> int:
    """
    Run a command as a subprocess with optional environment variables.

    Args:
        command (list): The command to run as a list of strings.
        env_vars (dict, optional): Additional environment variables to set.

    Raises:
        CalledProcessError: If the command fails.
    """
    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)
    try:
        run(command, env=env, check=True)
    except CalledProcessError as _error:
        raise _error


def run_python(script: list[str], env_vars: Optional[dict] = None):
    """
    Run a Python script as a subprocess.
    """
    run_command(["python", script], env_vars)


def run_ipynb(script: list[str], env_vars: Optional[dict] = None):
    """
    Run a Jupyter notebook as a subprocess by converting it to a script first.
    """
    run_command(
        ["jupyter", "nbconvert", "--to", "script", script, "--execute"], env_vars
    )


def run_streamlit(script: list[str], env_vars: Optional[dict] = None):
    """
    Run a Streamlit app as a subprocess.
    """
    run_command(["streamlit", "run", script], env_vars)


class PipelineError(Exception):
    """Exception raised for errors in the pipeline."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def run_stage(_stage: str):
    """
    Run a stage of the pipeline.

    Args:
        _stage (str): The path to the stage to run.
    """
    if not os.path.exists(_stage):
        raise PipelineError(f"Stage not found: {_stage}")

    # https://regex101.com/r/JFd40X/1
    pattern = r"^(?!.*\/[^\/]*\.[^\/]*$).*\/([^\/]+)$"
    match_dir_path_only = re.match(pattern, _stage)

    if _stage.endswith(".py") or match_dir_path_only:
        run_python(_stage)
    elif _stage.endswith(".ipynb"):
        run_ipynb(_stage)
    elif _stage.endswith(".py"):
        run_streamlit(_stage)
    else:
        raise ValueError(f"Unsupported file type: {_stage}")


def log_and_print(message: str, logging_level: int = logging.INFO):
    """
    Logs a message at the specified logging level
    and prints it to the console with the current time.

    Args:
        message (str): The message to log and print.
        logging_level (int, optional): The logging level.

    Raises:
        ValueError: If the logging level is not supported.
    """

    if logging_level == logging.INFO:
        logging.info(message)
    elif logging_level == logging.WARNING:
        logging.warning(message)
    elif logging_level == logging.ERROR:
        logging.error(message)
    else:
        raise ValueError(f"Unsupported logging level: {logging_level}")

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{current_time}: {message}")


if __name__ == "__main__":
    load_dotenv()  # Load environment variables from .env

    scraping = [os.path.join("pipeline", "src", "a_scraping")]
    cleaning_stage = os.path.join("pipeline", "src", "b_cleaning")
    cleaning_sub_stageg = [
        os.path.join(cleaning_stage, "a_cleaning_OLX.ipynb"),
        os.path.join(cleaning_stage, "b_cleaning_OtoDom.ipynb"),
        os.path.join(cleaning_stage, "c_combining_data.ipynb"),
        os.path.join(cleaning_stage, "d_creating_map_data.ipynb"),
    ]
    model_developing = [
        os.path.join("pipeline", "src", "c_model_developing", "model_training.ipynb")
    ]
    data_visualizing = [
        os.path.join(
            "pipeline", "src", "d_data_visualizing", "dashboard", "streamlit_app.py"
        )
    ]

    stages = scraping + cleaning_sub_stageg + model_developing + data_visualizing

    for stage in stages:
        log_and_print(f"Running {stage}...")

        try:
            # Attempt to run the stage, which may raise CalledProcessError on failure
            run_stage(stage)
            log_and_print(f"{stage} completed successfully.")
        except CalledProcessError as error:
            # Log the error and terminate the pipeline on failure
            error_message = (
                f"Error in {stage} with exit code {error.returncode}. Exiting pipeline."
            )
            log_and_print(error_message, logging.ERROR)
            raise PipelineError(error_message) from error

    log_and_print("Pipeline execution completed.")
