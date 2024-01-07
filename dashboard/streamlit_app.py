# Standard imports
import os

# Third-party imports
import streamlit as st

# Local imports
from aesthetics import config as aesthetics_config
from load_data import DataLoader
from map_visualizer import MapVisualizer
from bar_chart_visualizer import BarChartVisualizer
from table_visualizer import TableVisualizer


def streamlit_app():
    your_offers_df, other_offers_df, map_offers_df = load_data()

    render_data(your_offers_df, other_offers_df, map_offers_df)


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

    if not check_if_file_exists(your_offers_path):
        return

    your_offers_df, other_offers_df, map_offers_df = data_processor.load_data(
        your_offers_path=your_offers_path
    )

    return your_offers_df, other_offers_df, map_offers_df


def render_data(your_offers_df, other_offers_df, map_offers_df):
    """
    Renders the data in the application.

    Args:
        your_offers_df (pd.DataFrame): A DataFrame containing your offers.
        other_offers_df (pd.DataFrame): A DataFrame containing other offers.
        map_offers_df (pd.DataFrame): A DataFrame containing offers for the map.

    Raises:
        Exception: If an unspecified error occurs.
    """
    st.set_page_config(layout="wide")

    display_title("🔍🏠 Rent comparisons")
    bar_chart_visualizer = BarChartVisualizer(
        aesthetics_config, your_offers_df, other_offers_df
    )
    bar_chart_visualizer.display()

    table_visualizer = TableVisualizer(aesthetics_config)
    table_visualizer.display(your_offers_df, other_offers_df)

    map_visualizer = MapVisualizer(aesthetics_config)
    map_visualizer.display(
        map_offers_df,
        "🗺️ Property Prices Heatmap",
        center_coords=(50.460740, 19.093210),
        center_marker_name="Mierzęcice, Będziński, Śląskie",
        zoom=9,
    )


def display_title(title: str):
    st.markdown(
        f"<h1 style='text-align: center;'>{title}</h1>",
        unsafe_allow_html=True,
    )


def check_if_file_exists(your_offers_path):
    # Check if the environment variable was set
    if your_offers_path is None:
        st.error(
            "The environment variable 'YOUR_OFFERS_PATH' is not set. Please set the variable and try again."
        )
        return False

    # Check if the file exists
    if not os.path.isfile(your_offers_path):
        st.error(f"The file specified does not exist: {your_offers_path}")
        return False

    # Check if the file is a CSV
    if not your_offers_path.lower().endswith(".csv"):
        st.error("The file specified is not a CSV file.")
        return False

    return True


streamlit_app()
