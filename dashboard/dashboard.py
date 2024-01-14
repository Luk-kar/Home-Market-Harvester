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


class DataVisualizer:
    def __init__(
        self, user_apartments_df, market_apartments_df, map_offers_df, aesthetics_config
    ):
        """
        Initializes the dashboard with necessary data.

        Args:
            user_apartments_df (pd.DataFrame): A DataFrame containing your offers.
            market_apartments_df (pd.DataFrame): A DataFrame containing other offers.
            map_offers_df (pd.DataFrame): A DataFrame containing offers for the map.
            aesthetics_config: Configuration for the aesthetics of the visualizations.
        """
        self.user_apartments_df = user_apartments_df
        self.market_apartments_df = market_apartments_df
        self.map_offers_df = map_offers_df
        self.aesthetics_config = aesthetics_config
        st.set_page_config(layout="wide")

    def render_data(self):
        """
        Renders the data in the application.
        Raises:
            Exception: If an unspecified error occurs.
        """
        self.display_title("🔍🏠 Rent comparisons")

        bar_chart_visualizer = BarChartVisualizer(
            self.aesthetics_config, self.user_apartments_df, self.market_apartments_df
        )
        bar_chart_visualizer.display()

        table_visualizer = TableVisualizer(self.aesthetics_config)
        table_visualizer.display(self.user_apartments_df, self.market_apartments_df)

        map_visualizer = MapVisualizer(self.aesthetics_config)
        map_visualizer.display(
            self.map_offers_df,
            "🗺️ Property Prices Heatmap",
            center_coords=(50.460740, 19.093210),
            center_marker_name="Mierzęcice, Będziński, Śląskie",
            zoom=9,
        )

    @staticmethod
    def display_title(title: str):
        """
        Displays a title in the application.

        Args:
            title (str): The title to display.
        """
        st.markdown(
            f"<h1 style='text-align: center;'>{title}</h1>",
            unsafe_allow_html=True,
        )
