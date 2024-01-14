# Third-party imports
import streamlit as st

# Local imports
from _config import config as display_settings
from map_visualizer import MapVisualizer
from bar_chart_visualizer import BarChartVisualizer
from table_visualizer import TableVisualizer


class DataVisualizer:
    def __init__(
        self,
        user_apartments_df,
        market_apartments_df,
        map_offers_df,
        display_settings,
        dashboard_title,
    ):
        """
        Initializes the dashboard with necessary data.

        Args:
            user_apartments_df (pd.DataFrame): A DataFrame containing your offers.
            market_apartments_df (pd.DataFrame): A DataFrame containing other offers.
            map_offers_df (pd.DataFrame): A DataFrame containing offers for the map.
            display_settings: Configuration for the display settings of the visualizations.
            dashboard_title (str): The title of the dashboard.
        """
        self.user_apartments_df = user_apartments_df
        self.market_apartments_df = market_apartments_df
        self.map_offers_df = map_offers_df
        self.display_settings = display_settings
        self.dashboard_title = dashboard_title

    def render_data(self):
        """
        Renders the data in the application.
        Raises:
            Exception: If an unspecified error occurs.
        """
        st.set_page_config(layout=display_settings["layout"])

        self.display_title(self.dashboard_title)

        bar_chart_visualizer = BarChartVisualizer(
            self.display_settings, self.user_apartments_df, self.market_apartments_df
        )
        bar_chart_visualizer.display()

        table_visualizer = TableVisualizer(self.display_settings)
        table_visualizer.display(self.user_apartments_df, self.market_apartments_df)

        map_visualizer = MapVisualizer(self.display_settings)
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
