# Local imports
from aesthetics import config as aesthetics_config
from dashboard.load_data import DataLoader
from dashboard.map_visualizer import MapVisualizer
from dashboard.bar_chart_visualizer import BarChartVisualizer
from dashboard.table_visualizer import TableVisualizer

if __name__ == "__main__":
    data_processor = DataLoader()
    your_offers_df, other_offers_df, map_offers_df = data_processor.load_data()

    bar_chart_visualizer = BarChartVisualizer(
        aesthetics_config, your_offers_df, other_offers_df
    )
    bar_chart_visualizer.display()

    map_visualizer = MapVisualizer(aesthetics_config)
    map_visualizer.display(map_offers_df)

    table_visualizer = TableVisualizer(aesthetics_config)
    table_visualizer.display(your_offers_df, other_offers_df)
