# Standard imports
import os

# Third-party imports
import streamlit as st

# Local imports
from _config import config as display_settings
from load_data import DataLoader
from dashboard.data_visualizer.data_visualizer import DataVisualizer


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
        "🔍🏠 Rent comparisons",
    ).render_data()


def load_data():
    """
    Loads data from the given CSV file path, converts data types, and creates additional data fields.

    Returns:
        tuple: A tuple containing DataFrames for your offers, other offers, and map offers.

    Raises:
        pd.errors.EmptyDataError: If the CSV file is empty.
        pd.errors.ParserError: If there is an error parsing the CSV file.
        Exception: If an unspecified error occurs.
    """
    data_processor = DataLoader()

    your_offers_path = os.getenv("YOUR_OFFERS_PATH", "data\\test\\your_offers.csv")

    if not _check_if_file_exists(your_offers_path):
        return

    user_apartments_df, market_apartments_df, map_offers_df = data_processor.load_data(
        your_offers_path=your_offers_path
    )

    return user_apartments_df, market_apartments_df, map_offers_df


def _check_if_file_exists(file_path: str):
    # Check if the environment variable was set
    if file_path is None:
        st.error(
            "The environment variable 'YOUR_OFFERS_PATH' is not set. Please set the variable and try again."
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
