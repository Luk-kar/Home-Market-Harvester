"""
This module provides logging functionalities for a data processing pipeline,
enabling both file-based and console logging with configurable levels of detail.
It is designed to facilitate tracking of the pipeline's execution status,
errors, and warnings by writing logs to a file 
and simultaneously printing them to the console.
"""

# Standard library imports
import logging
from datetime import datetime
from pathlib import Path


def setup_logging():
    """
    Sets up logging to write to a file with UTF-8 encoding.
    """

    root_project_path = Path(__file__).resolve().parents[2]
    log_file_path = root_project_path / "logs" / "pipeline.log"

    logging.basicConfig(
        filename=str(log_file_path),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode="a",  # Append mode
        encoding="utf-8",
    )


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
