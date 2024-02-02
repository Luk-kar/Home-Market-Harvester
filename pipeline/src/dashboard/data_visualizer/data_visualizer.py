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

    Args:
        user_apartments_df (pd.DataFrame): The user apartment data.
        market_apartments_df (pd.DataFrame): The market apartment data.
        map_offers_df (pd.DataFrame): The map offers data.
        display_settings (dict): The display settings for the dashboard.
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
        self.texts = Translation()

    def render_data(self):
        """
        Renders the data in the application.

        Raises:
            Exception: If an unspecified error occurs.
        """
        st.set_page_config(layout=self.display_settings["layout"])

        self.selected_language = self.render_language_selector()
        Translation.set_language(self.selected_language)

        self.display_title(self.texts["app_title"])

        bar_chart_visualizer = BarChartVisualizer(
            self.display_settings,
            self.user_apartments_df,
            self.market_apartments_df,
            self.texts["bar_chart"]["main_title"],
        )
        bar_chart_visualizer.display()

        st.markdown("---")

        table_visualizer = TableVisualizer(
            self.display_settings,
            (
                self.texts["table"]["main_title"],
                self.texts["table"]["subtitle"],
            ),
        )
        table_visualizer.display(self.user_apartments_df, self.market_apartments_df)

        st.markdown("---")

        map_visualizer = MapVisualizer(self.display_settings)
        map_visualizer.display(
            self.map_offers_df,
            self.texts["map"]["main_title"],
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
