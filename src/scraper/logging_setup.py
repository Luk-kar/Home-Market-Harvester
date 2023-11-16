import os
import logging
from config import LOGGING


def log_setup():
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
