"""
This module provides a class, ModelPredictor, for loading a machine learning model and its
metadata, preparing dataframes for prediction, and performing predictions using the model.

Example Usage:
--------------

model_path = "notebooks\\gbm_model_file.p"
metadata_path = "notebooks\\gbm_model_metadata.json"
user_offers_path = os.getenv("USER_OFFERS_PATH", "data\\test\\your_offers.csv")

predictor = ModelPredictor(model_path, metadata_path)
predictor.get_price_predictions(user_offers_path)

"""

# Standard imports
from datetime import datetime

# Third-party imports
import numpy as np
import pandas as pd

# Local imports
from model.model_io_operations import ModelManager


class ModelPredictor:
    """
    A class to load a machine learning model and its associated metadata, prepare dataframes
    for prediction, and perform predictions using the model.

    Args:
        model_path (str): Path to the saved model file.
        metadata_path (str): Path to the JSON file containing metadata about the model.

    Attributes:
        model: The loaded machine learning model.
        metadata (dict): The loaded metadata including column names and data types.

    Methods:
        get_price_predictions(offers_path): Loads offers data, predicts prices, and displays results.

    Example Usage:
    --------------

    model_path = "data\\model.pkl"
    offers_path = os.getenv("USER_OFFERS_PATH", "data\\test\\your_offers.csv")
    user_apartments_df = pd.read_csv(offers_path)

    predictor = ModelPredictor(model_path)
    predictor.get_price_predictions(user_apartments_df)
    """

    def __init__(self, model_path: str):
        model_manager = ModelManager(model_path)
        model, metadata = model_manager.load_model_and_metadata()

        # raise error if model or metadata is not loaded
        if model is None or metadata is None:
            raise RuntimeError("Model or metadata not loaded.")

        # raise error if model is not a sklearn model
        if not hasattr(model, "predict"):
            raise RuntimeError("Model does not have a predict method.")

        # raise error if metadata is not a dictionary
        if not isinstance(metadata, dict):
            raise RuntimeError("Metadata is not a dictionary.")

        self.model = model
        self.metadata = metadata

    def get_price_predictions(self, offers_df: pd.DataFrame) -> pd.Series:
        """
        Loads offers data, predicts prices, and displays results.

        Args:
            offers_df (pd.DataFrame): A DataFrame containing offers data.

        Returns:
            pd.Series: A Series containing the predicted prices.

        Raises:
            ValueError: If the offers_df is not a pandas DataFrame.
            RuntimeError: If the model or metadata is not loaded.
            ValueError: If prediction fails.

        Example Usage:
        --------------

        model_path = "notebooks\\lm_model_metadata.p"
        metadata_path = "notebooks\\lm_model.json"
        offers_path = os.getenv("USER_OFFERS_PATH", "data\\test\\your_offers.csv")
        user_apartments_df = pd.read_csv(offers_path)

        predictor = ModelPredictor(model_path, metadata_path)
        predictor.get_price_predictions(user_apartments_df)
        """

        if not isinstance(offers_df, pd.DataFrame):
            raise ValueError("offers_df must be a pandas DataFrame.")

        if self.model is None or self.metadata is None:
            raise RuntimeError("Model or metadata not loaded.")

        model_data = self._predict_prices(offers_df)
        if model_data is None:
            raise ValueError("Prediction failed.")

        total_price = model_data * offers_df["area"]
        return total_price

    def _calculate_building_age(self, build_year_series: pd.Series) -> pd.Series:
        """
        Convert a series of building years to building ages.

        :param build_year_series: A pandas Series containing building years.
        :return: A pandas Series containing building ages.
        """
        current_year = datetime.now().year

        # Calculate the age of the building by subtracting the year from the current year
        # If the value is np.nan, it remains np.nan
        building_age_series = build_year_series.apply(
            lambda x: current_year - x if np.isfinite(x) else np.nan
        )

        return building_age_series

    def _prepare_dataframe(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame.")

        try:
            # Create a copy of the dataframe to avoid modifying the original
            temp_df = df.copy()

            # Check if 'area' column exists and rename it to 'square_meters'
            if "area" in temp_df.columns:
                temp_df.rename(columns={"area": "square_meters"}, inplace=True)
            elif "square_meters" not in temp_df.columns:
                raise ValueError("'area' column not found in the DataFrame.")

            # Assuming narrowed_df is a DataFrame with MultiIndex columns
            new_values = self._calculate_building_age(temp_df["build_year"])
            temp_df.loc[:, "build_year"] = new_values

            # Add missing columns with default values
            for col, dtype in self.metadata["columns"].items():
                if col not in temp_df.columns:
                    default_value = 0 if pd.api.types.is_numeric_dtype(dtype) else None
                    temp_df[col] = default_value

            # Ensure all required columns are present
            missing_required_columns = set(self.metadata["column_order"]) - set(
                temp_df.columns
            )
            if missing_required_columns:
                raise ValueError(
                    f"Missing required columns in DataFrame: {missing_required_columns}"
                )

            # Remove extra columns that are not in the metadata's column order
            temp_df = temp_df[self.metadata["column_order"]]

            # Convert columns to the appropriate dtype
            for col, dtype in self.metadata["columns"].items():
                try:
                    temp_df[col] = temp_df[col].astype(dtype)
                except ValueError as error:
                    raise ValueError(
                        f"Column '{col}' cannot be converted to {dtype}"
                    ) from error

            return temp_df
        except Exception as error:
            raise ValueError(f"Error preparing dataframe: {error}") from error

    def _predict_prices(self, df: pd.DataFrame) -> pd.Series:
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame.")
        try:
            # Prepare the data frame
            prepared_df = self._prepare_dataframe(df)

            if prepared_df is not None:
                # Predict using the model
                predictions = self.model.predict(prepared_df)
                return predictions
            else:
                return None
        except Exception as error:
            raise ValueError(f"Error predicting prices: {error}") from error
