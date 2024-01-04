# Standard imports
import pandas as pd
import numpy as np

# Local imports
from ..notebooks._csv_utils import data_timeplace, DataPathCleaningManager


class DataLoader:
    def __init__(self):
        self.data_path_manager = DataPathCleaningManager(data_timeplace)

    def load_data(self):
        your_offers_df = pd.read_csv("../to_compare_example_data.csv")

        self._convert_data_types(your_offers_df)

        self._create_additional_data_types(your_offers_df)

        other_offers_df = self.data_path_manager._load_cleaned_df(domain="combined")
        map_offers_df = self.data_path_manager.load_df("map", is_cleaned=True)

        return your_offers_df, other_offers_df, map_offers_df

    def _convert_data_types(self, your_offers_df):
        your_offers_df["flat_id"] = your_offers_df["flat_id"].astype("Int64")
        your_offers_df["floor"] = your_offers_df["floor"].astype("Int64")
        your_offers_df["area"] = your_offers_df["area"].astype("Float64")
        your_offers_df["is_furnished"] = your_offers_df["is_furnished"].astype("bool")
        your_offers_df["price"] = your_offers_df["price"].astype("Float64")

    def _create_additional_data_types(self, your_offers_df):
        your_offers_df["price_per_meter"] = your_offers_df.apply(
            lambda row: round(row["price"] / row["area"], 2)
            if pd.notna(row["price"]) and pd.notna(row["area"])
            else np.nan,
            axis=1,
        )
