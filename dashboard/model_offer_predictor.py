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
        load_model_and_metadata(): Loads the model and metadata from specified paths.
        prepare_dataframe(df): Prepares a dataframe for prediction based on the model metadata.
        predict_and_merge(df): Performs prediction on the dataframe and merges results.
        get_price_predictions(your_offers_path): Loads offers data, predicts prices, and displays results.
    """

    def __init__(self, model_path: str, metadata_path: str):
        self.model, self.metadata = self._load_model_and_metadata(
            model_path, metadata_path
        )

    def get_price_predictions(self, offers_path: str):
        """
        Loads the machine learning model and its associated metadata from the specified file paths.

        The model is expected to be a pickled file, and metadata is expected in JSON format.
        This method sets the 'model' and 'metadata' attributes of the instance.

        Returns:
            tuple: A tuple containing the loaded model and metadata. If an error occurs during
            loading, returns (None, None).
        """

        if self.model is not None and self.metadata is not None:
            your_offers_df = pd.read_csv(offers_path)  # Load your offers dataframe
            result_df = self._predict_and_merge(your_offers_df)

            if result_df is not None:
                print("Prediction successful. Dataframe with suggested prices:")
                print(result_df.head())
            else:
                print("Prediction failed.")
        else:
            print("Model or metadata loading failed.")

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
                    print("Metadata file size exceeds the limit of 10 MB.")
                    return None, None
                metadata = json.loads(file_content)

            return model, metadata
        except Exception as e:
            print(f"Error loading model or metadata: {e}")
            return None, None

    def _prepare_dataframe(self, df: pd.DataFrame):
        try:
            # Create a copy of the dataframe to avoid modifying the original
            temp_df = df.copy()

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
            print(f"Error in preparing dataframe: {e}")
            return None

    def _predict_and_merge(self, df: pd.DataFrame):
        try:
            # Prepare the data frame
            prepared_df = self._prepare_dataframe(df)

            if prepared_df is not None:
                # Predict using the model
                predictions = self.model.predict(prepared_df)
                df["suggested_price"] = predictions

                return df
            else:
                return None
        except Exception as e:
            print(f"Error in model prediction: {e}")
            return None
