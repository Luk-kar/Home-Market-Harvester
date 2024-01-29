"""
This module contains the Streamlit application for the Home Market Harvester dashboard.
"""

# Standard imports
import os
import sys

# Third-party imports
import streamlit as st


def add_project_root_to_sys_path():
    """
    Adds the project root to the system path.
    """
    current_script_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(current_script_path))
    sys.path.insert(0, project_root)


# You have to add the project root to the system path
# before importing from it
add_project_root_to_sys_path()

# For the first runtime you need a relative import else error import
# Local imports
from data_visualizer._config import config as display_settings
from data_visualizer.data_visualizer import DataVisualizer
from load_data import DataLoader


def streamlit_app():
    """
    Main function for the Streamlit application.
    """
    user_apartments_df, market_apartments_df, map_offers_df = load_data()

    DataVisualizer(
        user_apartments_df,
        market_apartments_df,
        map_offers_df,
        display_settings,
    ).render_data()


def load_data():
    """
    Loads data from a CSV file specified
    by the 'YOUR_OFFERS_PATH' environment variable, converts data types,
    and creates additional data fields.
    If the environment variable is not set,
    it defaults to 'data\\test\\your_offers.csv'.

    First, it checks if the specified file exists.
    If it does not exist, it returns a tuple of None values.
    If the file exists, it proceeds to load the data,
    process it, and return the processed data in a tuple.

    Returns:
        tuple: A tuple containing DataFrames
               for your offers, market offers, and map offers.
               If the specified file does not exist or an error occurs,
               returns a tuple of None values.

    Raises:
        pd.errors.EmptyDataError: If the CSV file is empty.
        pd.errors.ParserError: If there is an error parsing the CSV file.
        FileNotFoundError: If the specified file does not exist.
        IOError: If an I/O error occurs while reading the file.
        Exception: For any other unspecified errors that occur during data processing.
    """
    data_processor = DataLoader()

    your_offers_path = os.getenv("YOUR_OFFERS_PATH", "data\\test\\your_offers.csv")

    if not _check_if_file_exists(your_offers_path):
        return None, None, None

    user_apartments_df, market_apartments_df, map_offers_df = data_processor.load_data(
        your_offers_path=your_offers_path
    )

    return user_apartments_df, market_apartments_df, map_offers_df


def _check_if_file_exists(file_path: str):
    """
    Checks if the specified file exists and is a CSV file.

    Args:
        file_path (str): The path to the file.

    Returns:
        bool: True if the file exists and is a CSV file, False otherwise.
    """
    # Check if the environment variable was set
    if file_path is None:
        st.error(
            "The environment variable 'YOUR_OFFERS_PATH' is not set. "
            + "Please set the variable and try again."
        )
        return False

    # Check if the file exists
    if not os.path.isfile(file_path):
        st.error(f"The file specified does not exist: {file_path}")
        return False

    # Check if the file is a CSV
    if not file_path.lower().endswith(".csv"):
        st.error("The file specified is not a CSV file.")
        return False

    return True


streamlit_app()
