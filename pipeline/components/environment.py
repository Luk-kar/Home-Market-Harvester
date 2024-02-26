"""
This module provides functionality to initialize and validate environment settings for a project,
mainly focusing on creating and ensuring the integrity of a .env file containing essential configuration
details. It includes mechanisms to validate, update, and manage environment variables critical for the
application's operation.
"""

# Standard library imports
from pathlib import Path
import logging
import re
import sys

# Local imports
from pipeline.components.logger import log_and_print, setup_logging

setup_logging()


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
        "LOCATION_QUERY=Warszawa\n"  # Be sure that location fits the query
        "AREA_RADIUS=25\n"  # 0, 5, 10, 15, 25, 50, 75
        "SCRAPED_OFFERS_CAP=5\n"  # Sky is the limit
        f"USER_OFFERS_PATH={str(Path('data') / 'test' / 'your_offers.csv')}\n"
        "CHROME_DRIVER_PATH=\n"  # path to the ChromeDriver
        "CHROME_BROWSER_PATH=\n"  # path to the Chrome browser
        "STREAMLIT_SERVER_PORT=8501\n"  # Default port for Streamlit
    )

    if not env_path.exists():
        log_and_print(
            f"The .env file was not found at {env_path}. Creating a new one with dummy data.",
            level="warning",
        )
        with open(env_path, "w", encoding=encoding) as file:
            file.write(env_content)

    validate_environment_variables(env_path, encoding)

    if env_path.read_text(encoding=encoding) == env_content:
        message = (
            "Please fill in the .env file with your data.\n"
            "Now the .env is just a template with dummy data.\n"
            f"The file {env_path} is located at the root of the project.\n"
            "Reload the environment settings."
        )
        log_and_print(message, logging.WARNING)
        raise ValueError(message)


def validate_environment_variables(env_path: Path, encoding: str = "utf-8"):
    """
    Validates that essential environment variables are set in the .env file.

    Args:
        env_path (Path): The path to the .env file.
        encoding (str, optional): The encoding used to read the .env file.

    Raises:
        ValueError: If any essential environment variable is missing, not set, or invalid.
    """
    # Load environment variables from the file
    env_content = env_path.read_text(encoding=encoding)

    # Define essential variables with optional validation rules
    essential_vars = {
        "AREA_RADIUS": {"allowed_values": [0, 5, 10, 15, 25, 50, 75]},
        "SCRAPED_OFFERS_CAP": {"is_digit": True},
        "USER_OFFERS_PATH": {"extension": ".csv"},
        "CHROME_DRIVER_PATH": {"check_exists": True},
        "CHROME_BROWSER_PATH": {"check_exists": True},
        "STREAMLIT_SERVER_PORT": {"is_port": True},
        # Add other variables as needed
    }

    # General validation for missing or empty variables
    for var, rules in essential_vars.items():
        pattern = rf"{var}=(.*)"
        match = re.search(pattern, env_content)
        if not match or not match.group(1).strip():
            message = f"The {var} environment variable is missing or not set in the .env file."
            log_and_print(message, logging.ERROR)
            raise ValueError(message)

        value = match.group(1).strip()
        path = Path(value) if "extension" in rules or "check_exists" in rules else None

        # Specific validations based on rules
        if ("extension" in rules) and (path.suffix != rules["extension"]):
            message = (
                f"The {var} is not set to a valid {rules['extension']} file.\n"
                f"The path is:\n{value}"
            )
            log_and_print(message, logging.ERROR)
            raise ValueError(message)

        if ("allowed_values" in rules) and (int(value) not in rules["allowed_values"]):
            message = (
                f"The {var} is set to an invalid value.\n"
                f"Allowed values are: {rules['allowed_values']}.\n"
                "The value is:\n"
                f"{value}"
            )
            log_and_print(message, logging.ERROR)
            raise ValueError(message)

        if ("is_digit" in rules) and (not value.isdigit()):
            message = f"The {var} must be a digit.\n" "The value is:\n" f"{value}"
            log_and_print(message, logging.ERROR)
            raise ValueError(message)

        if path and ("check_exists" in rules) and (not path.exists()):
            message = f"The {var} path does not exist:\n" f"{value}"
            log_and_print(message, logging.ERROR)
            raise ValueError(message)

        # Platform-specific checks for executables
        if (sys.platform == "win32") and (
            var in ["CHROME_DRIVER_PATH", "CHROME_BROWSER_PATH"]
            and path.suffix != ".exe"
        ):
            message = (
                f"The {var} on Windows must be an .exe file, but was set to:\n{value}"
            )
            log_and_print(message, logging.ERROR)
            raise ValueError(message)

        if ("is_port" in rules) and (
            not value.isdigit() or not (1 <= int(value) <= 65535)
        ):
            message = f"The {var} must be a valid port number (1-65535), but was set to:\n{value}"
            log_and_print(message, logging.ERROR)
            raise ValueError(message)


def update_environment_variable(env_path: Path, key: str, value: str):
    """
    Updates or adds an environment variable in the .env file.

    Args:
        env_path (Path): The path to the .env file.
        key (str): The environment variable key to update.
        value (str): The new value for the environment variable.
    """
    encoding = "utf-8"
    try:
        env_content = env_path.read_text(encoding=encoding)
    except FileNotFoundError:

        message = f"The .env file at {env_path} was not found. Please ensure the path is correct and the file exists."
        log_and_print(message, logging.ERROR)
        raise FileNotFoundError(message)
    except IOError as e:

        message = f"Failed to read the .env file at {env_path}. Error: {e}"
        log_and_print(message, logging.ERROR)
        raise IOError(message)

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
        raise ValueError(
            f"Error in regular expression.\n"
            "pattern:\n"
            f"{pattern}"
            "new_line:\n"
            f"{new_line}"
            "error:\n"
            f"{error}"
        ) from error

    try:
        env_path.write_text(env_content, encoding=encoding)
    except IOError as error:
        message = (
            f"Failed to write updates to the .env file at {env_path}.\nError: {error}"
        )
        log_and_print(message, logging.ERROR)
        raise IOError(message) from error


def set_user_data_path_env_var(
    user_data_path: str, env_path: Path, env_var_name: str = "USER_OFFERS_PATH"
) -> None:
    """
    Validates the user data file path provided in command line arguments
    and updates the corresponding environment variable
    in the .env file with this path.

    Args:
        args (argparse.Namespace): Parsed command line arguments
                                    containing the user data file path.
        env_path (Path): Path object pointing to the .env configuration file.
        env_var_name: The name of the environment variable to update with the user data path.
                      Defaults to "USER_OFFERS_PATH".

    Raises:
        FileNotFoundError: If the specified user data file does not exist at the provided path.
    """
    user_data_path = Path(user_data_path).resolve()

    if not user_data_path.exists():
        message = f"The user data file does not exist: {user_data_path}"
        log_and_print(message, logging.ERROR)
        raise ValueError(message)

    update_environment_variable(env_path, env_var_name, str(user_data_path))
