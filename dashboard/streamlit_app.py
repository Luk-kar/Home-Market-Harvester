# Third-party imports
import streamlit as st

# Local imports
from aesthetics import config as aesthetics_config
from load_data import DataLoader
from map_visualizer import MapVisualizer
from bar_chart_visualizer import BarChartVisualizer
from table_visualizer import TableVisualizer


def main():
    data_processor = DataLoader()
    your_offers_df, other_offers_df, map_offers_df = data_processor.load_data()

    st.set_page_config(layout="wide")

    display_title("🔍🏠 Rent comparisons")
    bar_chart_visualizer = BarChartVisualizer(
        aesthetics_config, your_offers_df, other_offers_df
    )
    bar_chart_visualizer.display()

    table_visualizer = TableVisualizer(aesthetics_config)
    table_visualizer.display(your_offers_df, other_offers_df)

    map_visualizer = MapVisualizer(aesthetics_config)
    map_visualizer.display(map_offers_df)


def display_title(title: str):
    st.markdown(
        f"<h1 style='text-align: center;'>{title}</h1>",
        unsafe_allow_html=True,
    )


main()
