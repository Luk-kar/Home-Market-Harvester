"""
This module contains the DataVisualizer class 
which is responsible for rendering data in the Streamlit application.

The DataVisualizer class takes in 
user and market apartment data, map offers data, display settings, and a dashboard title.
It provides methods to render the data in the application, 
display a title, and initialize the dashboard with necessary data.
"""

# Third-party imports
import streamlit as st

# Local imports
from dashboard.data_visualizer.map_visualizer import MapVisualizer
from dashboard.data_visualizer.bar_chart_visualizer import BarChartVisualizer
from dashboard.data_visualizer.table_visualizer.table_visualizer import TableVisualizer
from dashboard.translations.translation_manager import Translation, Languages


class DataVisualizer:
    """
    A class responsible for rendering data in the Streamlit application.

    Attributes:
        user_apartments_df (pd.DataFrame): A DataFrame containing your offers.
        market_apartments_df (pd.DataFrame): A DataFrame containing other offers.
        map_offers_df (pd.DataFrame): A DataFrame containing offers for the map.
        display_settings: Configuration for the display settings of the visualizations.
        dashboard_title (str): The title of the dashboard.
    """

    def __init__(
        self, user_apartments_df, market_apartments_df, map_offers_df, display_settings
    ):
        self.user_apartments_df = user_apartments_df
        self.market_apartments_df = market_apartments_df
        self.map_offers_df = map_offers_df
        self.display_settings = display_settings
        self.selected_language = None

    def render_data(self):
        """
        Renders the data in the application.

        Raises:
            Exception: If an unspecified error occurs.
        """
        st.set_page_config(layout=self.display_settings["layout"])

        self.selected_language = self.render_language_selector()
        Translation.set_language(self.selected_language)

        self.display_title(Translation()["app_title"])

        bar_chart_visualizer = BarChartVisualizer(
            self.display_settings,
            self.user_apartments_df,
            self.market_apartments_df,
            Translation()["char_chart"]["main_title"],
        )
        bar_chart_visualizer.display()

        table_visualizer = TableVisualizer(
            self.display_settings,
            (
                Translation()["table"]["main_title"],
                Translation()["table"]["subtitle"],
            ),
        )
        table_visualizer.display(self.user_apartments_df, self.market_apartments_df)

        map_visualizer = MapVisualizer(self.display_settings)
        map_visualizer.display(
            self.map_offers_df,
            Translation()["map"]["main_title"],
            center_coords=(50.460740, 19.093210),
            center_marker_name="Mierzęcice, Będziński, Śląskie",
            zoom=9,
        )

    def render_language_selector(self):
        """
        Renders the language selection dropdown in the Streamlit UI.
        """
        st.sidebar.header("Language Selector")
        selected_language = st.sidebar.selectbox(
            "Select Language", [Languages.ENGLISH, Languages.POLISH]
        )
        return selected_language

    def display_title(self, title: str):
        """
        Displays a title in the application.

        Args:
            title (str): The title to display.
        """
        st.markdown(
            f"<h1 style='text-align: center;'>{title}</h1>",
            unsafe_allow_html=True,
        )
