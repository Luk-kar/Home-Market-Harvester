"""
This module provides functionality for managing and verifying the presence of data within
specific directories, particularly focusing on the handling of raw data folders and CSV files
within data processing pipelines. It offers tools to scan directories for existing folders,
validate the presence of new data after a scraping stage, and ensure the existence of required
CSV files, thereby facilitating error-free data pipeline executions.
"""

# Standard library imports
from pathlib import Path
from typing import Set
import logging
import os

# Local imports
from pipeline.config._conf_file_manager import ConfigManager
from pipeline.components.exceptions import PipelineError
from pipeline.components.logger import log_and_print


def get_existing_folders(directory: Path) -> Set[str]:
    """
    Returns a set of existing folder names within the specified directory.

    Args:
        directory (Path): The directory to scan for folders.

    Returns:
        set[str]: A set containing the names of all folders found in the specified directory.
    """

    if not directory.exists() or not directory.is_dir():
        message = f"The specified directory does not exist: {directory}"
        log_and_print(message, logging.ERROR)
        raise FileNotFoundError(message)

    return {item.name for item in directory.iterdir() if item.is_dir()}


def get_pipeline_error_message(data_scraped_dir: Path):
    """
    Returns an error message for missing CSV files in the data/raw directory.

    Args:
        data_scraped_dir (Path): The directory where the required CSV files are missing.
    """
    return (
        "During the scraping stage, the following error occurred:\n"
        "Required CSV files not found in the data/raw directory:\n"
        f"{data_scraped_dir}\n"
        "Be sure that location query is correct:\n"
        f"{os.getenv('LOCATION_QUERY')}\n"
    )


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

    message = (
        "Expected a new folder to be created during scraping, but none was found:\n"
        f"data_raw_dir:\n{data_raw_dir}\n"
        f"initial_folders:\n{initial_folders}\n"
        f"current_folders:\n{current_folders}\n"
        f"new_folders:\n{new_folders if new_folders else None}\n"
    )
    log_and_print(message, logging.ERROR)
    raise PipelineError(message)


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
        message = get_pipeline_error_message(data_scraped_dir)
        log_and_print(message, logging.ERROR)
        raise PipelineError(message)


def set_destination_coordinates(destination: str):
    """
    Sets the destination coordinates in the configuration file.

    This function parses a string containing latitude and longitude, validates the format,
    the data type, and the range of the coordinates, and then writes these coordinates to
    a configuration file.

    Args:
        destination (str): A string containing latitude and longitude separated by a comma.

    Raises:
        ValueError: If the input string is not in the correct format, if the coordinates
                    are not valid numbers, or if the latitude and longitude are not in the
                    acceptable range (-90 to 90 for latitude and -180 to 180 for longitude).
        FileNotFoundError: If the configuration file does not exist.
        Exception: For other unexpected errors during the writing process to the configuration file.
    """
    destination_sanitized = sanitize_destination_coordinates(destination)

    try:
        config_manager = ConfigManager("run_pipeline.conf")
    except ValueError as ve:
        message = f"Failed to initialize configuration management:\n{ve}"
        log_and_print(message, logging.ERROR)
        raise ValueError(message) from ve

    except FileNotFoundError as fnfe:
        message = f"Configuration file not found:\n{fnfe}"
        log_and_print(message, logging.ERROR)
        raise FileNotFoundError(message) from fnfe

    try:
        config_manager.write_value(
            "DESTINATION_COORDINATES", str(destination_sanitized)
        )
    except Exception as unexpected_error:
        message = f"Failed to write destination coordinates to configuration file:\n{unexpected_error}"
        log_and_print(message, logging.ERROR)
        raise Exception(message) from unexpected_error


def sanitize_destination_coordinates(destination: str):
    """
    Sanitizes the input string containing destination coordinates.

    This function parses a string containing latitude and longitude, validates the format,
    the data type, and the range of the coordinates.

    Args:
        destination (str): A string containing latitude and longitude separated by a comma.

    Returns:
        tuple: A tuple containing the sanitized latitude and longitude coordinates.

    Raises:
        ValueError: If the input string is not in the correct format, if the coordinates
                    are not valid numbers, or if the latitude and longitude are not in the
                    acceptable range (-90 to 90 for latitude and -180 to 180 for longitude).
    """
    destination_split = [coord.strip(" ()") for coord in destination.split(",")]

    error_message = (
        "The destination coordinates should be provided as latitude and longitude separated by a comma.\n"
        f"Parsed input: {destination_split}"
    )
    if len(destination_split) != 2:
        log_and_print(error_message, logging.ERROR)
        raise ValueError(error_message)

    try:
        destination_sanitized = tuple([float(coord) for coord in destination_split])
    except ValueError:
        log_and_print(error_message, logging.ERROR)
        raise ValueError(
            "Both latitude and longitude must be valid numbers.\n"
            f"Parsed input: {destination_split}"
        )

    # Validate latitude and longitude ranges
    latitude, longitude = destination_sanitized

    if not -90 <= latitude <= 90:
        message = f"Latitude must be between -90 and 90 degrees. Value: {latitude}"
        log_and_print(message, logging.ERROR)
        raise ValueError(message)

    if not -180 <= longitude <= 180:
        message = f"Longitude must be between -180 and 180 degrees. Value: {longitude}"
        log_and_print(message, logging.ERROR)

        raise ValueError(message)

    return destination_sanitized
