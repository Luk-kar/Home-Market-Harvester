# Standard imports
import os
import sys
import pandas as pd
import numpy as np

# Third-party imports
import streamlit as st


# Local imports
def add_project_root_to_sys_path():
    current_script_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(current_script_path))
    sys.path.insert(0, project_root)


add_project_root_to_sys_path()

from notebooks._csv_utils import data_timeplace, DataPathCleaningManager


class DataLoader:
    """
    DataLoader is responsible for loading and preparing data for the application.

    It manages the paths for data files, loads data from CSV files, and preprocesses
    the data by converting data types and creating additional data fields.

    Attributes:
        data_path_manager (DataPathCleaningManager): A manager that handles the paths to data files
                                                     and provides utilities for cleaning data paths.
    """

    def __init__(self):
        data_path_manager = DataPathCleaningManager(data_timeplace)
        self._update_paths(data_path_manager.paths, "..\\data", "data")
        self.data_path_manager = data_path_manager

    def load_data(self, your_offers_path):
        """
        Loads data from the given CSV file path, converts data types, and creates additional data fields.

        Args:
            your_offers_path (str): The file path to your offers CSV file.

        Returns:
            tuple: A tuple containing DataFrames for your offers, other offers, and map offers.

        Raises:
            pd.errors.EmptyDataError: If the CSV file is empty.
            pd.errors.ParserError: If there is an error parsing the CSV file.
            Exception: If an unspecified error occurs.
        """
        try:
            your_offers_df = pd.read_csv(your_offers_path)

            self._convert_data_types(your_offers_df)

            self._create_additional_data_types(your_offers_df)

            other_offers_df = self.data_path_manager._load_cleaned_df(domain="combined")
            map_offers_df = self.data_path_manager.load_df("map", is_cleaned=True)

            return your_offers_df, other_offers_df, map_offers_df

        except pd.errors.EmptyDataError:
            st.error(f"The file is empty: {your_offers_path}")
        except pd.errors.ParserError:
            st.error(
                f"There was a parsing error when trying to read the file: {your_offers_path}"
            )
        except Exception as e:
            st.error(f"An error occurred when trying to read the file: {e}")

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
