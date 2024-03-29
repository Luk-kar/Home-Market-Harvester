"""
This module provides a simple interface for managing configuration settings through a file-based system.
It includes a custom exception class for handling missing or empty configuration values and a `ConfigManager`
class designed to facilitate the reading and writing of key-value pairs stored within a configuration file.
"""

# Standard imports
import os


class ConfKeyError(Exception):
    """Custom exception for missing or empty configuration values."""

    pass


class ConfigManager:
    """
    A class for managing read and write operations on a configuration file.
    This class allows for easy access and modification of settings stored in
    a simple key-value pair format within the configuration file.

    Attributes:
    - config_path (str): The path to the configuration file.

    Raises:
    - ValueError: If the configuration file format is invalid.
    - FileNotFoundError: If the specified configuration file does not exist.
    """

    def __init__(self, config_name: str):
        """
        Initializes the ConfigManager with the path to the configuration file.

        Args:
        - config_path (str): The path to the configuration file.

        Raises:
        - ValueError: If the configuration file format is invalid.
        - FileNotFoundError: If the specified configuration file does not exist.

        Notes:
        - When the configuration file does not exist,
        a new file is created with the specified name.
        """

        # get the file directory path
        file_dir = os.path.dirname(os.path.realpath(__file__))

        if not config_name.endswith(".conf"):
            message = (
                "Invalid configuration file format. Only .conf files are supported."
            )
            raise ValueError(message)

        config_file_path = os.path.join(file_dir, config_name)

        self.config_path = config_file_path
        self.encoding = "utf-8"

        if not os.path.exists(config_file_path):

            if "run_pipeline.conf" == config_name:
                config_content = "MARKET_OFFERS_TIMEPLACE=\n" "DESTINATION_COORDINATES"
            else:
                config_content = ""

            with open(config_file_path, "w", encoding=self.encoding) as file:
                file.write(config_content)

    def read_value(self, key_to_find: str) -> str:
        """
        Reads the value of a given key from the configuration file.

        Parameters:
        - key_to_find: The key whose value is to be read.

        Returns:
        - The value corresponding to the key if found.

        Raises:
        - ConfigKeyError: If the key is not found or the value is empty.
        """
        with open(self.config_path, "r", encoding=self.encoding) as file:
            for line in file:
                if line.startswith(key_to_find):
                    key_value_pair = line.split("=", 1)
                    value = key_value_pair[1].strip()
                    is_value_emptish = value == ""
                    if len(key_value_pair) > 1 and not is_value_emptish:
                        return value
                    else:
                        message = (
                            f"Value for key '{key_to_find}' is empty or not found."
                        )
                        raise ConfKeyError(message)

        # If the loop completes without returning, the key was not found
        message = f"Key '{key_to_find}' not found in configuration."
        raise ConfKeyError(message)

    def write_value(self, key: str, value: str):
        """
        Writes or updates a key-value pair in the configuration file.
        If the key already exists, its value is updated. Otherwise, a new key-value pair is added.

        Parameters:
        - key: The key to be added or updated.
        - value: The value corresponding to the key.
        """

        lines = []
        with open(self.config_path, "r", encoding=self.encoding) as file:
            lines = file.readlines()

        key_found = False
        for i, line in enumerate(lines):
            if line.startswith(key):
                lines[i] = f"{key}={value}\n"
                key_found = True
                break

        if not key_found:
            lines.append(f"{key}={value}\n")

        with open(self.config_path, "w", encoding=self.encoding) as file:
            file.writelines(lines)
