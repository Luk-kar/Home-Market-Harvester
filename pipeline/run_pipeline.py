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
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from typing import Union, Optional, Set
import argparse
import logging
import os
import re
import subprocess
import sys
import time


def set_sys_path_to_project_root(__file__: str):
    """
    Adds the project root to the system path.

    Args:
        __file__ (str): The path to the current file.
    """
    root_dir = Path(__file__).resolve().parent
    sys.path.append(str(root_dir))


set_sys_path_to_project_root(__file__)

# Local imports
from config._config_manager import ConfigManager


def setup_logging():
    """
    Sets up logging to write to a file with UTF-8 encoding.
    """
    logging.basicConfig(
        filename=str(Path("logs") / "pipeline.log"),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode="a",  # Append mode
        encoding="utf-8",
    )


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


def run_command(command: list[str], env_vars: Optional[dict] = None) -> int:
    """
    Run a command as a subprocess with optional environment variables
    and an option to ignore non-zero exit codes.

    Args:
        command (list[str]): The command to run as a list of strings.
        env_vars (dict, optional): Additional environment variables to set.

    Returns:
        int: The exit code of the subprocess.

    Raises:
        subprocess.CalledProcessError: If the subprocess call fails.
    """

    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)

    result = subprocess.run(
        command, env=env, check=False
    )  # Use check=False to manually handle exit codes
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, command)
    return result.returncode


def run_python(script: str, env_vars: dict, args: Optional[list] = None) -> int:
    """
    Run a Python script as a subprocess with optional command-line arguments.

    Args:
        script (str): The path to the Python script to run.
        env_vars (dict): Additional environment variables to set for the script.
        args (list, optional): A list of command-line arguments to pass to the script.

    Returns:
        int: The exit code of the subprocess.
    """
    command = ["python", script]
    if args:
        command.extend(args)

    exit_code = run_command(command, env_vars)

    return exit_code


def run_ipynb(_stage: str, env_vars: dict):
    """
    Run a Jupyter notebook as a subprocess by converting it to a script first.
    The execution uses the `pipenv` environment.

    Args:
        _stage (str): The path to the Jupyter notebook to run.
        env_vars (dict): Additional environment variables to set for the notebook.

    Returns:
        int: The exit code of the subprocess.
    """

    notebook_path = Path(_stage).resolve()

    # Command to convert and execute the notebook using nbconvert within pipenv
    command = [
        "pipenv",
        "run",
        "jupyter",
        "nbconvert",
        "--to",
        "script",
        "--execute",
        "--output-dir",
        str(notebook_path.parent),
        str(notebook_path),
    ]

    # Run the command
    exit_code = run_command(command, env_vars)

    return exit_code


def run_streamlit(script: list[str], env_vars: dict):
    """
    Run a Streamlit app as a subprocess and monitor its output to log when it's successfully initialized.

    Args:
        script (str): The path to the Streamlit script.
        env_vars (dict): Environment variables to set for the subprocess.

    WARNING:
        This function starts the Streamlit server as a non-blocking concurrent process.
        It is important to manage this process by monitoring its output for successful initialization
        and ensuring it is properly terminated when no longer needed.
        Failure to terminate the Streamlit process can result in resource leaks
        and unintended operation of the application.
        It is recommended to track the process ID and implement
        a mechanism to terminate the process based on the application's lifecycle or user action.
    """
    env = os.environ.copy()
    env.update(env_vars)

    # Start Streamlit as a subprocess and capture its output
    process = subprocess.Popen(
        ["streamlit", "run", script],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )

    # Monitor the subprocess output for a success message
    while True:
        output = process.stdout.readline()
        print(output, end="")  # Optional: print Streamlit's output to console
        if "You can now view your Streamlit app in your browser." in output:
            log_and_print("Streamlit app initialized successfully.")
            # WARNING about concurrent process management
            log_and_print(
                "WARNING: Streamlit app is running as a concurrent process. "
                "Ensure it is terminated appropriately when no longer needed.",
                logging.WARNING,
            )
            break
        if process.poll() is not None:
            log_and_print("Streamlit app failed to start.", logging.ERROR)
            break
        time.sleep(0.1)  # Avoid busy waiting

    return process


class PipelineError(Exception):
    """Exception raised for errors in the pipeline."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def run_stage(_stage: str, env_vars: dict, args: Optional[list] = None):
    """
    Run a stage of the pipeline.

    Args:
        _stage (str): The path to the stage to run.
        env_vars (dict): The environment variables to set.
        args (list, optional): Additional arguments to pass to the stage.

    Returns:
        subprocess.Popen: The process object for the Streamlit app, if applicable.

    Raises:
        PipelineError: If the stage is not found or fails.
    """
    if not Path(_stage).exists():
        raise PipelineError(f"Stage not found: {_stage}")

    # https://regex101.com/r/nY3BlO/1/r/JFd40X/1
    pattern = r"^(?!.*[/\\][^/\\]*\.[^/\\]*$).*[/\\]([^/\\]+)$"
    match_dir_path_only = re.match(pattern, _stage)

    args_valid_type = None
    if args:
        args_valid_type = [str(arg) for arg in args] if args else None

    process = None
    exit_code = None

    try:
        if (
            _stage.endswith(".py") and not _stage.endswith("streamlit_app.py")
        ) or match_dir_path_only:
            exit_code = run_python(_stage, env_vars, args_valid_type)
        elif _stage.endswith(".ipynb"):
            exit_code = run_ipynb(_stage, env_vars)
        elif _stage.endswith("streamlit_app.py"):
            process = run_streamlit(_stage, env_vars)
        else:
            raise ValueError(f"Unsupported file type: {_stage}")

        if exit_code is not None and exit_code != 0:
            log_and_print(
                f"Stage {_stage} completed with exit code {exit_code}.", logging.WARNING
            )

    except subprocess.CalledProcessError as error:
        log_and_print(
            f"Error in {_stage} with exit code {error.returncode}.", logging.ERROR
        )
        raise PipelineError(f"Error in {_stage}. Exiting pipeline.") from error

    return process


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


def update_environment_variable(_env_path: Path, key: str, value: str):
    """
    Updates or adds an environment variable in the .env file.

    Args:
        _env_path (Path): The path to the .env file.
        key (str): The environment variable key to update.
        value (str): The new value for the environment variable.
    """
    encoding = "utf-8"
    env_content = _env_path.read_text(encoding=encoding)

    safe_value = value.replace(
        "\\", "\\\\"
    )  # Escape backslashes for safe regex and file writing
    new_line = f"{key}={safe_value}\n"

    # Properly escape the key for regex pattern
    escaped_key = re.escape(key)
    pattern = rf"^{escaped_key}=.*\n"

    try:
        # If key exists, replace its line using a regex pattern that accounts for multiline
        if re.search(pattern, env_content, flags=re.MULTILINE):
            env_content = re.sub(pattern, new_line, env_content, flags=re.MULTILINE)
        else:
            # If key doesn't exist, append it
            env_content += new_line
    except re.error as error:
        raise ValueError(f"Error in regular expression: {error}")

    _env_path.write_text(env_content, encoding=encoding)


def get_existing_folders(directory: Path) -> Set[str]:
    """
    Returns a set of existing folder names within the specified directory.

    Args:
        directory (Path): The directory to scan for folders.

    Returns:
        set[str]: A set containing the names of all folders found in the specified directory.
    """

    if not directory.exists() or not directory.is_dir():
        raise FileNotFoundError(f"The specified directory does not exist: {directory}")

    return {item.name for item in directory.iterdir() if item.is_dir()}


def get_pipeline_error_message(_stage: str, data_scraped_dir: Path):
    """
    Returns an error message for missing CSV files in the data/raw directory.
    """
    return (
        "Required CSV files not found in the data/raw directory:\n"
        f"{data_scraped_dir}\n"
        "Stage:\n"
        f"{_stage}\n"
        "Be sure that location query is correct:\n"
        f"{os.getenv('LOCATION_QUERY')}\n"
    )


def set_user_data_path_env_var(
    args: argparse.Namespace, env_path: Path, env_var_name: str = "USER_OFFERS_PATH"
) -> None:
    """
    Validates the user data file path provided in command line arguments
    and updates the corresponding environment variable
    in the .env file with this path.

    Args:
        args (argparse.Namespace): Parsed command line arguments containing the user data file path.
        env_path (Path): Path object pointing to the .env configuration file.
        env_var_name: The name of the environment variable to update with the user data path. Defaults to "USER_OFFERS_PATH".

    Raises:
        FileNotFoundError: If the specified user data file does not exist at the provided path.
    """
    user_data_path = Path(args.user_data_path).resolve()
    if not user_data_path.exists():
        raise ValueError(f"The user data file does not exist: {user_data_path}")
    update_environment_variable(env_path, env_var_name, str(user_data_path))


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
        help=f"The radius of the area for scraping in kilometers. Defaults to {default_args['area_radius']}.",
    )

    parser.add_argument(
        "--scraped_offers_cap",
        type=int,
        default=default_args["scraped_offers_cap"],
        help=f"The maximum number of offers to scrape. Defaults to {default_args['scraped_offers_cap']}.",
    )
    parser.add_argument(
        "--user_data_path",
        type=str,
        nargs="?",
        help="The path to the user data file in CSV format to display in the dashboard.",
    )

    args = parser.parse_args()
    return args


def decide_skip_based_on_files(
    stage: str, data_raw_dir: Path, config_file: ConfigManager
) -> bool:
    """
    Determines if a cleaning stage for OLX or Otodom should be skipped based on the
    presence of the respective data files.

    Args:
        stage (str): The name of the current pipeline stage.
        data_raw_dir (Path): The directory where raw data is stored.
        config_file (ConfigManager): A configuration manager instance to access configuration values.

    Returns:
        bool: True if the stage should be skipped, False otherwise.

    Raises:
        PipelineError: If neither OLX nor Otodom data files are found.
        ValueError: If the stage is not supported.
    """

    MARKET_OFFERS_TIMEPLACE = config_file.read_value("MARKET_OFFERS_TIMEPLACE")
    data_scraped_dir = data_raw_dir / MARKET_OFFERS_TIMEPLACE
    olx_exists = any(data_scraped_dir.glob("olx.pl.csv"))
    otodom_exists = any(data_scraped_dir.glob("otodom.pl.csv"))

    if not olx_exists and not otodom_exists:
        raise PipelineError(get_pipeline_error_message(stage, data_scraped_dir))

    stages = {"OLX": "a_cleaning_OLX", "otodom": "b_cleaning_otodom"}

    if not any(stage_identifier in stage for stage_identifier in stages.values()):
        raise ValueError(f"Unsupported stage: {stage}")

    if stages["OLX"] in stage and not olx_exists:
        log_and_print("Skipping OLX cleaning due to missing olx.pl.csv file.")
        return True

    elif stages["otodom"] in stage and not otodom_exists:
        log_and_print("Skipping Otodom cleaning due to missing otodom.pl.csv file.")
        return True

    else:
        return False


def is_relevant_cleaning_stage(stage: str) -> bool:
    """
    Determines if the given stage is a cleaning stage for OLX or Otodom and should be skipped.

    Args:
        stage (str): The name of the current pipeline stage.

    Returns:
        bool: True if the stage is a cleaning stage for OLX or Otodom and should be skipped, False otherwise.
    """
    is_cleaning_stage = "b_cleaning" in stage
    is_relevant_platform = "OLX" in stage or "otodom" in stage
    return is_cleaning_stage and is_relevant_platform


def run_pipeline(
    stages: list[str],
    args: argparse.Namespace,
    config_file: ConfigManager,
    data_raw_dir: Path,
):
    """
    Executes the defined pipeline stages.

    Args:
        stages (List[str]): A list of stage names to run.
        args (argparse.Namespace): The parsed command-line arguments required for the stages.
        config_file (ConfigManager): The configuration manager instance for accessing configuration values.
        data_raw_dir (Path): The directory where raw data is stored.
    """
    streamlit_process = None
    for stage in stages:
        skip_stage = is_relevant_cleaning_stage(stage) and decide_skip_based_on_files(
            stage, data_raw_dir, config_file
        )
        if skip_stage:
            continue

        log_and_print(f"Running {stage}...")
        try:
            process_stage(stage, args, streamlit_process, data_raw_dir, config_file)

        except PipelineError as e:
            log_and_print(f"Error running {stage}: {e}", logging.ERROR)
            break  # Exit the loop on error

    else:
        log_and_print("Pipeline execution completed.")


def process_stage(
    stage: str,
    args: argparse.Namespace,
    streamlit_process: None,
    data_raw_dir: Path,
    config_file: ConfigManager,
):
    """
    Processes a given pipeline stage based on its type (scraping, streamlit app, etc.).

    Args:
        stage (str): The name of the stage to process.
        args (Any): Arguments required for the stage.
        streamlit_process (None: The current streamlit process, if applicable.
        data_raw_dir (Path): Path to the directory where raw data is stored.
        config_file (ConfigManager): The configuration manager for accessing and updating config values.
    """
    if "a_scraping" in stage:
        scraping_args = [
            "--location_query",
            args.location_query,
            "--area_radius",
            args.area_radius,
            "--scraped_offers_cap",
            args.scraped_offers_cap,
        ]

        initial_folders = get_existing_folders(data_raw_dir)

        run_stage(stage, os.environ, scraping_args)
        update_after_scraping(data_raw_dir, config_file, initial_folders)
    elif "streamlit_app" in stage:
        handle_streamlit_app(stage, streamlit_process)
    else:
        run_stage(stage, os.environ)


def handle_streamlit_app(stage: str, streamlit_process: None):
    """
    Handles the execution of a Streamlit app stage within the pipeline.

    Args:
        stage (str): The name of the stage, expected to be a Streamlit app.
        streamlit_process (Optional[Any]): The Streamlit process to manage, if already running.
    """
    streamlit_process = run_stage(stage, os.environ)
    manage_streamlit_process(streamlit_process)


def manage_streamlit_process(streamlit_process: subprocess.Popen):
    """
    Provides an interface for managing the lifecycle of a Streamlit process.

    Args:
        streamlit_process (subprocess.Popen): The Streamlit process to manage.
    """

    print("Type 'stop' and press Enter to terminate the Dashboard and its server:")
    while True:
        user_input = input().strip().lower()
        if user_input == "stop":
            terminate_streamlit(streamlit_process)
            break
        else:
            print(
                "Unrecognized command. Type 'stop' and press Enter to terminate the Dashboard:"
            )


def terminate_streamlit(streamlit_process: subprocess.Popen):
    """
    Terminates the Streamlit process.

    Args:
        streamlit_process (subprocess.Popen): The Streamlit process to terminate.
    """

    try:
        streamlit_process.terminate()
        streamlit_process.wait()
        log_and_print("Dashboard has been terminated.")
    except KeyboardInterrupt:
        handle_ctrl_c(streamlit_process)


def handle_ctrl_c(streamlit_process: subprocess.Popen):
    """
    Handles a KeyboardInterrupt event by terminating the Streamlit process.

    Args:
        streamlit_process (subprocess.Popen): The Streamlit process to terminate.
    """

    print("\nCtrl+C detected. Terminating the Dashboard...")
    streamlit_process.terminate()
    streamlit_process.wait()
    log_and_print("Dashboard has been terminated due to Ctrl+C.")
    sys.exit(1)


def update_after_scraping(
    data_raw_dir: Path, config_file: ConfigManager, initial_folders: Set[str]
):
    """
    Updates the configuration file after scraping based on the newly created folders.

    Args:
        data_raw_dir (Path): Path to the directory where raw data is stored.
        config_file (ConfigManager): The configuration manager for accessing and updating config values.
        initial_folders (Set[str]): A set of folder names present before the scraping stage.
    """

    new_folder = check_new_csv_files(data_raw_dir, initial_folders)

    if new_folder and new_folder != config_file.read_value("MARKET_OFFERS_TIMEPLACE"):

        log_and_print(
            f"New folder found: {new_folder}. Updating the configuration file."
            f'Writing "MARKET_OFFERS_TIMEPLACE"={new_folder} to {config_file.config_path}'
        )

        config_file.write_value("MARKET_OFFERS_TIMEPLACE", new_folder)
    else:
        log_and_print(
            "No new folders were found after scraping. Exiting the pipeline.",
            logging.WARNING,
        )
        exit(1)


def check_new_csv_files(data_raw_dir: Path, initial_folders: Set[str]) -> str:
    """
    Checks for new CSV files in the raw data directory
    and identifies the newly created folder.

    Args:
        data_raw_dir (Path): Path to the directory where raw data is stored.
        initial_folders (Set[str]): A set of folder names present before the scraping stage.

    Returns:
        str: The name of the newly created folder.

    Raises:
        PipelineError: If no new folder is found or if multiple new folders are found.
    """

    current_folders = get_existing_folders(data_raw_dir)
    new_folders = current_folders - initial_folders

    if len(new_folders) == 1:
        new_folder_name = new_folders.pop()
        data_scraped_dir = data_raw_dir / new_folder_name
        validate_csv_files_presence(data_scraped_dir)
        return new_folder_name
    raise PipelineError(
        "Expected a new folder to be created during scraping, but none was found:\n"
        f"data_raw_dir:\n{data_raw_dir}"
        f"initial_folders:\n{initial_folders}"
        f"current_folders:\n{current_folders}"
        f"new_folders:\n{new_folders if new_folders else None}\n"
    )


def validate_csv_files_presence(data_scraped_dir: Path):
    """
    Validates the presence of CSV files within a specified directory.
    It's used to ensure that expected data files are present after
    a scraping operation else raise a PipelineError.

    Args:
        data_scraped_dir (Path): The directory to check for CSV files.

    Raises:
        PipelineError: If no CSV files are found in the directory.
    """

    csv_files = list(data_scraped_dir.glob("*.csv"))
    if not csv_files:
        raise PipelineError(get_pipeline_error_message(data_scraped_dir))


if __name__ == "__main__":

    initialize_environment_settings()

    setup_logging()

    args = parse_arguments()

    env_path = Path(".env")
    if args.user_data_path:
        set_user_data_path_env_var(args, env_path, "USER_OFFERS_PATH")

    load_dotenv(dotenv_path=env_path)  # Load environment variables from .env

    stages = [
        str(Path("pipeline") / "src" / "a_scraping"),
        str(Path("pipeline") / "src" / "b_cleaning" / "a_cleaning_OLX.ipynb"),
        str(Path("pipeline") / "src" / "b_cleaning" / "b_cleaning_otodom.ipynb"),
        str(Path("pipeline") / "src" / "b_cleaning" / "c_combining_data.ipynb"),
        str(Path("pipeline") / "src" / "b_cleaning" / "d_creating_map_data.py"),
        str(Path("pipeline") / "src" / "c_model_developing" / "model_training.py"),
        str(Path("pipeline") / "src" / "d_data_visualizing" / "streamlit_app.py"),
    ]

    run_pipeline(stages, args, ConfigManager("run_pipeline.conf"), Path("data") / "raw")
