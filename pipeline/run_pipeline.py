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

    _env_path = Path(
        ".env"
    )  # Assuming the root of the project is the project directory
    encoding = "utf-8"

    env_content = (
        # A structure example
        f"USER_OFFERS_PATH={str(Path('data') / 'test' / 'your_offers.csv')}\n"
        "MARKET_OFFERS_TIMEPLACE=\n"  # To be created after the scraping stage
        "MODEL_PATH=model.pkl\n"  # To be created after model training
        "LOCATION_QUERY=Warszawa\n"  # Be sure that location fits the query
        "AREA_RADIUS=25\n"  # 0, 5, 10, 15, 25, 50, 75
        "SCRAPED_OFFERS_CAP=5\n"  # Sky is the limit
        "CHROME_DRIVER_PATH=\n"  # path to the ChromeDriver
        "CHROME_BROWSER_PATH=\n"  # path to the Chrome browser
    )

    if not _env_path.exists():
        with open(_env_path, "w", encoding=encoding) as file:
            file.write(env_content)

    validate_environment_variables(_env_path, encoding)

    if _env_path.read_text(encoding=encoding) == env_content:
        raise ValueError(
            "Please fill in the .env file with your data.\n"
            f"The file {_env_path} is located at the root of the project.\n"
            "Reload the environment settings."
        )


def validate_environment_variables(_env_path: Path, encoding: str = "utf-8"):
    """
    Validates that essential environment variables are set in the .env file.

    Args:
        env_path (Path): The path to the .env file.
        encoding (str, optional): The encoding used to read the .env file.

    Raises:
        ValueError: If any essential environment variable is missing, not set, or invalid.
    """
    # Load environment variables from the file
    env_content = _env_path.read_text(encoding=encoding)

    # Define essential variables with optional validation rules
    essential_vars = {
        "USER_OFFERS_PATH": {"extension": ".csv"},
        "MODEL_PATH": {"extension": ".pkl"},
        "AREA_RADIUS": {"allowed_values": [0, 5, 10, 15, 25, 50, 75]},
        "SCRAPED_OFFERS_CAP": {"is_digit": True},
        "CHROME_DRIVER_PATH": {"check_exists": True},
        "CHROME_BROWSER_PATH": {"check_exists": True},
        # Add other variables as needed
    }

    # General validation for missing or empty variables
    for var, rules in essential_vars.items():
        pattern = rf"{var}=(.*)"
        match = re.search(pattern, env_content)
        if not match or not match.group(1).strip():
            raise ValueError(
                f"The {var} environment variable is missing or not set in the .env file."
            )

        value = match.group(1).strip()
        path = Path(value) if "extension" in rules or "check_exists" in rules else None

        # Specific validations based on rules
        if ("extension" in rules) and (path.suffix != rules["extension"]):
            raise ValueError(
                f"The {var} is not set to a valid {rules['extension']} file."
            )

        if ("allowed_values" in rules) and (int(value) not in rules["allowed_values"]):
            raise ValueError(
                (
                    f"The {var} is set to an invalid value."
                    "Allowed values are: {rules['allowed_values']}."
                )
            )

        if ("is_digit" in rules) and (not value.isdigit()):
            raise ValueError(f"The {var} must be a digit.")

        if path and ("check_exists" in rules) and (not path.exists()):
            raise ValueError(f"The {var} path does not exist: {value}")

        # Platform-specific checks for executables
        if (sys.platform == "win32") and (
            var in ["CHROME_DRIVER_PATH", "CHROME_BROWSER_PATH"]
            and path.suffix != ".exe"
        ):
            raise ValueError(f"The {var} on Windows must be an .exe file.")


initialize_environment_settings()

logging.basicConfig(
    filename=str(Path("logs") / "pipeline.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
)


def run_command(
    command: list[str], env_vars: Optional[dict] = None, ignore_exit_code: bool = False
) -> int:
    """
    Run a command as a subprocess with optional environment variables
    and an option to ignore non-zero exit codes.

    Args:
        command (list[str]): The command to run as a list of strings.
        env_vars (dict, optional): Additional environment variables to set.
        ignore_exit_code (bool, optional): If True, non-zero exit codes will not raise an exception.
        Defaults to False.

    Returns:
        int: The exit code of the subprocess.

    Raises:
        CalledProcessError: If the command fails and ignore_exit_code is False.
    """

    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)

    result = run(
        command, env=env, check=False
    )  # Use check=False to manually handle exit codes
    if result.returncode != 0 and not ignore_exit_code:
        raise CalledProcessError(result.returncode, command)
    return result.returncode


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

    Raises:
        PipelineError: If the stage is not found or fails.
    """
    if not Path(_stage).exists():
        raise PipelineError(f"Stage not found: {_stage}")

    # https://regex101.com/r/JFd40X/1
    pattern = r"^(?!.*\/[^\/]*\.[^\/]*$).*\/([^\/]+)$"
    match_dir_path_only = re.match(pattern, _stage)

    exit_code = None
    try:
        if _stage.endswith(".py") or match_dir_path_only:
            run_python(_stage)
        elif _stage.endswith(".ipynb"):
            run_ipynb(_stage)
        elif _stage.endswith(".py"):
            run_streamlit(_stage)
        else:
            raise ValueError(f"Unsupported file type: {_stage}")

        if exit_code != 0:
            log_and_print(
                f"Stage {_stage} completed with exit code {exit_code}.", logging.WARNING
            )

    except CalledProcessError as error:
        log_and_print(
            f"Error in {_stage} with exit code {error.returncode}.", logging.ERROR
        )
        raise PipelineError(f"Error in {_stage}. Exiting pipeline.") from error


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
    env_path = Path(".env")
    load_dotenv(dotenv_path=env_path)  # Load environment variables from .env

    scraping = [str(Path("pipeline") / "src" / "a_scraping")]
    CLEANING_STAGE = str(Path("pipeline") / "src" / "b_cleaning")
    cleaning_sub_stages = [
        str(Path(CLEANING_STAGE) / "a_cleaning_OLX.ipynb"),
        str(Path(CLEANING_STAGE) / "b_cleaning_OtoDom.ipynb"),
        str(Path(CLEANING_STAGE) / "c_combining_data.ipynb"),
        str(Path(CLEANING_STAGE) / "d_creating_map_data.ipynb"),
    ]
    model_developing = [
        str(Path("pipeline") / "src" / "c_model_developing" / "model_training.ipynb")
    ]
    data_visualizing = [
        str(
            Path("pipeline")
            / "src"
            / "d_data_visualizing"
            / "dashboard"
            / "streamlit_app.py"
        )
    ]

    stages = scraping + cleaning_sub_stages + model_developing + data_visualizing

    for stage in stages:
        log_and_print(f"Running {stage}...")
        run_stage(stage)
        log_and_print(f"{stage} completed successfully.")

    log_and_print("Pipeline execution completed.")
