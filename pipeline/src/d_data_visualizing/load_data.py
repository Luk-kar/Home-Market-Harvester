"""
This module provides functionality for data loading and preprocessing for a real estate application. 
It includes the DataLoader class, which is responsible for loading, preparing, 
and processing real estate offer data. 
The class manages paths for data files, loads data from CSV files, 
and preprocesses the data by converting data types and creating additional data fields.

The module handles data related to user-submitted apartment offers and market offers, 
facilitating various data operations like loading data from CSV files, type conversion, 
and computation of additional metrics such as price per meter. 
It also incorporates error handling for common issues encountered during data loading and parsing.
"""

# Standard imports
from pathlib import Path
import numpy as np
import pandas as pd

# Third-party imports
import streamlit as st


# Local imports
from pipeline.src._csv_utils import (
    DataPathCleaningManager,
)  # pylint: disable=wrong-import-position


class DataLoader:
    """
    DataLoader is responsible for loading and preparing data for the application.

    It manages the paths for data files, loads data from CSV files, and preprocesses
    the data by converting data types and creating additional data fields.

    Args:
        data_timeplace (str): The timestamp of the market offers data.
        user_offers_path (str): The path to the CSV file containing your offers.

    Attributes:
        data_path_manager (DataPathCleaningManager): The data path manager.
        user_offers_path (str): The path to the CSV file containing your offers.
    """

    def __init__(self, data_timeplace: str, user_offers_path: str, project_root: Path):
        data_path_manager = DataPathCleaningManager(data_timeplace, project_root)
        self.user_offers_path = user_offers_path
        self.data_path_manager = data_path_manager

    def load_data(self):
        """
        Loads data from the given CSV file path, converts data types,
        and creates additional data fields.

        Returns:
            tuple of pd.DataFrame: A tuple containing three pandas DataFrames:
                                   one each for user offers, market offers, and map offers.

        Raises:
            pd.errors.EmptyDataError: Raised if the CSV file is empty.
            pd.errors.ParserError: Raised if there is an error parsing the CSV file.
            FileNotFoundError: Raised if the specified user offers file does not exist.
            IOError: Raised if an I/O error occurs while reading the file.
            Exception: Raised for any other unspecified errors that occur during data processing.
        """
        try:
            user_apartments_df = pd.read_csv(self.user_offers_path)

            self._convert_data_types(user_apartments_df)

            self._create_additional_data_types(user_apartments_df)

            market_apartments_df = self.data_path_manager.load_cleaned_df(
                domain="combined"
            )

            map_offers_df = self.data_path_manager.load_df("map", is_cleaned=True)

            return user_apartments_df, market_apartments_df, map_offers_df

        except pd.errors.EmptyDataError:
            st.error(f"The file is empty: {self.user_offers_path}")
        except pd.errors.ParserError:
            st.error(
                f"There was a parsing error when trying to read the file: {self.user_offers_path}"
            )
        except FileNotFoundError:
            st.error(f"The file was not found: {self.user_offers_path}")
        except IOError:
            st.error(
                f"An I/O error occurred when trying to read the file: {self.user_offers_path}"
            )

        raise Exception("An unspecified error occurred.")

    def _convert_data_types(self, user_apartments_df: pd.DataFrame):
        """
        Convert data types of the user apartments DataFrame.

        Args:
            user_apartments_df (pd.DataFrame): A DataFrame containing your offers.
        """
        user_apartments_df["flat_id"] = user_apartments_df["flat_id"].astype("string")
        user_apartments_df["floor"] = user_apartments_df["floor"].astype("Int64")
        user_apartments_df["area"] = user_apartments_df["area"].astype("Float64")
        user_apartments_df["is_furnished"] = user_apartments_df["is_furnished"].astype(
            "bool"
        )
        user_apartments_df["price"] = user_apartments_df["price"].astype("Float64")

    def _create_additional_data_types(self, user_apartments_df: pd.DataFrame):
        """
        Create additional data fields for the user apartments DataFrame.

        Args:
            user_apartments_df (pd.DataFrame): A DataFrame containing your offers.
        """
        user_apartments_df["price_per_meter"] = user_apartments_df.apply(
            lambda row: (
                round(row["price"] / row["area"], 2)
                if pd.notna(row["price"]) and pd.notna(row["area"])
                else np.nan
            ),
            axis=1,
        )
