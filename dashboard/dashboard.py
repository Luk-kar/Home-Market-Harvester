import streamlit as st


class Dashboard:
    def __init__(self, data_processor, map_visualizer, bar_chart_visualizer):
        self.data_processor = data_processor
        self.map_visualizer = map_visualizer
        self.bar_chart_visualizer = bar_chart_visualizer

    def display_title(self, title):
        st.markdown(
            f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True
        )

    def display_bar_charts(self, your_offers_df, other_offers_df):
        self.bar_chart_visualizer.display_bar_chart(your_offers_df, other_offers_df)

    def display_table(self, your_offers_df, other_offers_df):
        # This method should create and display tables based on the data.
        # Implement the logic based on your requirements.
        pass

    def display_map(self, map_offers_df):
        self.map_visualizer.show_property_map(
            map_offers_df,
            "Property Prices Heatmap",
            center_coords=(50.460740, 19.093210),
            center_marker_name="Mierzęcice, Będziński, Śląskie",
            zoom=9,
        )

    def render_dashboard(self):
        st.set_page_config(layout="wide")
        self.display_title("🔍🏠 Rent Comparisons")

        your_offers_df, other_offers_df, map_offers_df = self.data_processor.load_data()

        self.display_bar_charts(your_offers_df, other_offers_df)

        self.display_table(your_offers_df, other_offers_df)

        self.display_map(map_offers_df)
