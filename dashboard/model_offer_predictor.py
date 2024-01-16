"""
This module provides a class, ModelPredictor, for loading a machine learning model and its
metadata, preparing dataframes for prediction, and performing predictions using the model.

Example Usage:
--------------

model_path = "notebooks\\gbm_model_file.p"
metadata_path = "notebooks\\gbm_model_metadata.json"
your_offers_path = os.getenv("YOUR_OFFERS_PATH", "data\\test\\your_offers.csv")

predictor = ModelPredictor(model_path, metadata_path)
predictor.get_price_predictions(your_offers_path)

"""

# Standard imports
import json

# Third-party imports
import pandas as pd
import pickle


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

    model_path = "notebooks\\lm_model_file.p"
    metadata_path = "notebooks\\lm_model_metadata.json"
    offers_path = os.getenv("YOUR_OFFERS_PATH", "data\\test\\your_offers.csv")
    user_apartments_df = pd.read_csv(offers_path)

    predictor = ModelPredictor(model_path, metadata_path)
    predictor.get_price_predictions(user_apartments_df)
    """

    def __init__(self, model_path: str, metadata_path: str):
        self.model, self.metadata = self._load_model_and_metadata(
            model_path, metadata_path
        )

    def get_price_predictions(self, offers_df: pd.DataFrame) -> pd.Series:
        """
        Loads offers data, predicts prices, and displays results.

        Args:
            offers_df (pd.DataFrame): A DataFrame containing offers data.

        Returns:
            pd.Series: A Series containing the predicted prices.

        Raises:
            Exception: If an unspecified error occurs.

        Example Usage:
        --------------

        model_path = "notebooks\\lm_model_metadata.p"
        metadata_path = "notebooks\\lm_model.json"
        offers_path = os.getenv("YOUR_OFFERS_PATH", "data\\test\\your_offers.csv")
        user_apartments_df = pd.read_csv(offers_path)

        predictor = ModelPredictor(model_path, metadata_path)
        predictor.get_price_predictions(user_apartments_df)
        """

        if not isinstance(offers_df, pd.DataFrame):
            raise ValueError("offers_df must be a pandas DataFrame.")

        if self.model is not None and self.metadata is not None:
            model_data = self._predict_prices(offers_df)

            if model_data is not None:
                total_price = model_data * offers_df["area"]
                return total_price
            else:
                raise Exception("Prediction failed.")
        else:
            raise Exception("Model or metadata not loaded.")

    def _load_model_and_metadata(self, model_path: str, metadata_path: str):
        try:
            # Load the trained model
            with open(model_path, "rb") as pickled:
                data = pickle.load(pickled)
                model = data["model"]

            # Load the metadata with size limitation for security
            max_metadata_size = 10 * 1024 * 1024  # 10 MB size limit
            with open(metadata_path, "r") as file:
                file_content = file.read(
                    max_metadata_size
                )  # Read only the first 10 MB of the file
                if file.tell() >= max_metadata_size:
                    raise ValueError("Metadata file size exceeded limit.")
                metadata = json.loads(file_content)

            return model, metadata
        except Exception as e:
            raise ValueError(f"Error loading model and metadata: {e}")

    def _prepare_dataframe(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame.")

        try:
            # Create a copy of the dataframe to avoid modifying the original
            temp_df = df.copy()

            # rename column area to square_meters
            temp_df.rename(columns={"area": "square_meters"}, inplace=True)

            # Add missing columns with default values
            for col, dtype in self.metadata["columns"].items():
                if col not in temp_df.columns:
                    default_value = 0 if dtype != "object" else "False"
                    temp_df[col] = default_value

            # Convert columns to the appropriate dtype
            for col, dtype in self.metadata["columns"].items():
                temp_df[col] = temp_df[col].astype(dtype)

            # Reorder columns as per the model
            temp_df = temp_df[self.metadata["column_order"]]

            return temp_df
        except Exception as e:
            raise ValueError(f"Error preparing dataframe: {e}")

    def _predict_prices(self, df: pd.DataFrame) -> pd.Series:
        try:
            # Prepare the data frame
            prepared_df = self._prepare_dataframe(df)

            if prepared_df is not None:
                # Predict using the model
                predictions = self.model.predict(prepared_df)
                return predictions
            else:
                return None
        except Exception as e:
            raise ValueError(f"Error predicting prices: {e}")
