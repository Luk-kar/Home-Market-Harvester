"""
This module provides functionality for managing and verifying the presence of data within
specific directories, particularly focusing on the handling of raw data folders and CSV files
within data processing pipelines. It offers tools to scan directories for existing folders,
validate the presence of new data after a scraping stage, and ensure the existence of required
CSV files, thereby facilitating error-free data pipeline executions.
"""

# Standard library imports
import os
from pathlib import Path
from typing import Set

# Local imports
from pipeline.components.exceptions import PipelineError


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
