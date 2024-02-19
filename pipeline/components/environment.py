"""
This module provides functionality to initialize and validate environment settings for a project,
mainly focusing on creating and ensuring the integrity of a .env file containing essential configuration
details. It includes mechanisms to validate, update, and manage environment variables critical for the
application's operation.
"""

# Standard library imports
import argparse
import re
import sys
from pathlib import Path


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
        f"USER_OFFERS_PATH={str(Path('data') / 'test' / 'your_offers.csv')}\n"
        "MODEL_PATH=model.pkl\n"  # To be created after model training
        "LOCATION_QUERY=Warszawa\n"  # Be sure that location fits the query
        "AREA_RADIUS=25\n"  # 0, 5, 10, 15, 25, 50, 75
        "SCRAPED_OFFERS_CAP=5\n"  # Sky is the limit
        "CHROME_DRIVER_PATH=\n"  # path to the ChromeDriver
        "CHROME_BROWSER_PATH=\n"  # path to the Chrome browser
        "STREAMLIT_SERVER_PORT=8501\n"  # Default port for Streamlit
    )

    if not env_path.exists():
        with open(env_path, "w", encoding=encoding) as file:
            file.write(env_content)

    validate_environment_variables(env_path, encoding)

    if env_path.read_text(encoding=encoding) == env_content:
        raise ValueError(
            "Please fill in the .env file with your data.\n"
            f"The file {env_path} is located at the root of the project.\n"
            "Reload the environment settings."
        )


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
        "USER_OFFERS_PATH": {"extension": ".csv"},
        "AREA_RADIUS": {"allowed_values": [0, 5, 10, 15, 25, 50, 75]},
        "SCRAPED_OFFERS_CAP": {"is_digit": True},
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

        if ("is_port" in rules) and (
            not value.isdigit() or not (1 <= int(value) <= 65535)
        ):
            raise ValueError(
                f"The {var} must be a valid port number (1-65535), but was set to: {value}"
            )


def update_environment_variable(env_path: Path, key: str, value: str):
    """
    Updates or adds an environment variable in the .env file.

    Args:
        env_path (Path): The path to the .env file.
        key (str): The environment variable key to update.
        value (str): The new value for the environment variable.
    """
    encoding = "utf-8"
    env_content = env_path.read_text(encoding=encoding)

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
        raise ValueError(f"Error in regular expression: {error}") from error

    env_path.write_text(env_content, encoding=encoding)


def set_user_data_path_env_var(
    args: argparse.Namespace, env_path: Path, env_var_name: str = "USER_OFFERS_PATH"
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
    user_data_path = Path(args.user_data_path).resolve()
    if not user_data_path.exists():
        raise ValueError(f"The user data file does not exist: {user_data_path}")
    update_environment_variable(env_path, env_var_name, str(user_data_path))
