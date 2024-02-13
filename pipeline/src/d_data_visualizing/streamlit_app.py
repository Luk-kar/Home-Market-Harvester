"""pipeline\.src\.
This module contains the Streamlit application for the Home Market Harvester d_data_visualizing.
"""

# Standard imports
import os
import sys
from pathlib import Path

# Third-party imports
import streamlit as st


def set_project_root() -> Path:
    """
    Sets the project root and appends it to the system path.

    Returns:
        Path: The root directory of the project.
    """
    project_root = Path(__file__).resolve().parents[3]
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))
    return project_root


project_root = set_project_root()

# Local imports
from pipeline.src.d_data_visualizing.config import DATA
from pipeline.src.d_data_visualizing.data_visualizer._config import (
    config as display_settings,
)
from pipeline.src.d_data_visualizing.data_visualizer.data_visualizer import (
    DataVisualizer,
)
from pipeline.src.d_data_visualizing.load_data import DataLoader


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
    Loads data from a CSV file specified by the `config.py`.
    The function converts data types and
    creates additional data fields as part of the data processing.

    The function performs several steps:
    1. It checks if the specified file exists. If not, it raises a FileNotFoundError.
    2. If the file exists, it initializes a DataLoader with the market data datetime and path to the user offers.
    3. It then loads, processes, and returns the data in three separate DataFrames:
       one each for user offers, market offers, and map offers.

    Returns:
        tuple of pd.DataFrame: A tuple containing three pandas DataFrames:
            - The user offers.
            - The market offers.
            - The map offers.

    Raises:
        FileNotFoundError: If the specified user offers file does not exist.
        Exception: For any other unspecified errors that occur during data processing.
    """
    user_offers_path = DATA["user_data_path"]

    if not _check_if_file_exists(user_offers_path):
        raise FileNotFoundError(
            f"The specified file does not exist.\n{user_offers_path}"
        )

    data_loader = DataLoader(
        DATA["market_data_datetime"], user_offers_path, project_root
    )

    user_apartments_df, market_apartments_df, map_offers_df = data_loader.load_data()

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
            "The environment variable 'USER_OFFERS_PATH' is not set. "
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
