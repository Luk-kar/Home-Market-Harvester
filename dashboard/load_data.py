# Standard imports
import os
import sys
import pandas as pd
import numpy as np


# Local imports
def add_project_root_to_sys_path():
    current_script_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(current_script_path))
    sys.path.insert(0, project_root)


add_project_root_to_sys_path()

from notebooks._csv_utils import data_timeplace, DataPathCleaningManager


class DataLoader:
    def __init__(self):
        data_path_manager = DataPathCleaningManager(data_timeplace)
        self._update_paths(data_path_manager.paths, "..\\data", "data")
        self.data_path_manager = data_path_manager

    def load_data(self):
        your_offers_df = pd.read_csv("../to_compare_example_data.csv")

        self._convert_data_types(your_offers_df)

        self._create_additional_data_types(your_offers_df)

        other_offers_df = self.data_path_manager._load_cleaned_df(domain="combined")
        map_offers_df = self.data_path_manager.load_df("map", is_cleaned=True)

        return your_offers_df, other_offers_df, map_offers_df

    def _update_paths(self, d: dict, old_str: str, new_str: str) -> None:
        """
        Recursively updates all string values in a nested dictionary.
        """
        for key, value in d.items():
            if isinstance(value, dict):
                self._update_paths(
                    value, old_str, new_str
                )  # Corrected the method name here
            else:
                d[key] = value.replace(old_str, new_str)

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
