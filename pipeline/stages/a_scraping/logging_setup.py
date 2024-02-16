"""
This module configures logging for the application.
"""

# Standard imports
import logging
import os

# Local imports
from pipeline.stages.a_scraping.config import LOGGING


def log_setup():
    """
    Sets up logging for the application.

    It creates a logger object,
    sets its level,
    and adds two handlers for logging:
    one for writing logs to a file and
    another for console output.

    If the log directory does not exist, it is created.

    The log messages are formatted with
    time, log level, and the log message.
    """

    if not os.path.exists("./logs"):
        os.makedirs("./logs")

    # Create a logger object
    logger = logging.getLogger()
    logger.setLevel(LOGGING["level"])  # Set the log level

    # Create handlers - one for file output, one for console output
    file_handler = logging.FileHandler(LOGGING["file"])
    console_handler = logging.StreamHandler()

    # Create a logging format
    formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
