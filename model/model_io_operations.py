"""
Model Management Module

This module provides functionality for managing machine learning models
and their associated metadata. It includes capabilities to save and load
models, handle model metadata, and verify model loading. The module is
designed to work with models compatible with the scikit-learn framework,
although it can be adapted for use with other machine learning libraries.
"""

# Standard imports
import json
import pickle
import random
import os

# Third-party imports
from sklearn.base import BaseEstimator
import numpy as np
import pandas as pd


class ModelManager:
    """
    A class that manages the model and its metadata.

    Attributes:
        model_path (str): The path to the model file.
        model_metadata_file_path (str): The path to the model metadata file.

    Methods:
        save_dataframe_metadata: Save the column names, data types, and column order of any DataFrame to a JSON file.
        load_metadata: Load the metadata from a file.
        save_model: Save the model to a file.
        load_model: Load the model from a file.
        check_if_loaded_properly: Check if the loaded model can make predictions.
    """

    def __init__(
        self,
        model_path_IO: str,
        model: BaseEstimator,
        training_data: pd.DataFrame = None,
    ):
        # Check if the directory exists
        model_dir, model_dir_exists = self._model_dir_exists(model_path_IO)
        if not model_dir_exists:
            raise FileNotFoundError(f"The directory {model_dir} does not exist.")

        self.model_path_IO = model_path_IO
        self.model = model
        self.model_metadata_file_path = self._create_metadata_path(model_path_IO)
        self.training_data = training_data

    def save_all_files_required(self, df: pd.DataFrame = None):
        if df is None:
            df = self.training_data
            if df is None:
                raise ValueError(
                    "No DataFrame provided and no training data available."
                )

        self.save_dataframe_metadata(df)
        self.save_model(self.model)

    def load_model_and_metadata(self) -> (BaseEstimator, dict):
        model = self.load_model()
        metadata = self.load_metadata()
        return model, metadata

    def save_model(self, model: BaseEstimator = None, model_path_IO: str = None):
        if model is None:
            model = self.model
            if model is None:
                raise ValueError("No model provided and no model available.")
        if model_path_IO is None:
            model_path_IO = self.model_path_IO
            if model_path_IO is None:
                raise ValueError("No model path provided and no model path available.")
        try:
            pickl = {"model": model}
            with open(model_path_IO, "wb") as file:
                pickle.dump(pickl, file)
        except IOError as error:
            raise IOError(f"Error saving model: {error}") from error
        except Exception as error:
            raise RuntimeError(
                f"Unexpected error when saving model: {error}"
            ) from error

    def save_dataframe_metadata(self, df: pd.DataFrame = None):
        try:
            if df is None:
                df = self.training_data
                if df is None:
                    raise ValueError(
                        "No DataFrame provided and no training data available."
                    )

            metadata = {
                "columns": {col: str(df[col].dtype) for col in df.columns},
                "column_order": list(df.columns),
            }

            with open(self.model_metadata_file_path, "w") as file:
                json.dump(metadata, file, indent=4)
        except IOError as error:
            raise IOError(f"Error saving DataFrame metadata: {error}") from error
        except Exception as error:
            raise RuntimeError(
                f"Unexpected error when saving DataFrame metadata: {error}"
            ) from error

    def load_model(self) -> BaseEstimator:
        try:
            with open(self.model_path_IO, "rb") as pickled:
                data = pickle.load(pickled)
                return data.get("model")
        except FileNotFoundError as error:
            raise FileNotFoundError(
                f"Model file not found at {self.model_path_IO}"
            ) from error
        except pickle.UnpicklingError as error:
            raise pickle.UnpicklingError(f"Error loading model: {error}") from error
        except Exception as error:
            raise RuntimeError(
                f"Unexpected error when loading model: {error}"
            ) from error

    def load_metadata(self) -> dict:
        try:
            with open(self.model_metadata_file_path, "r") as file:
                return json.load(file)
        except FileNotFoundError as error:
            raise FileNotFoundError(
                f"Metadata file not found at {self.model_metadata_file_path}"
            ) from error
        except json.JSONDecodeError as error:
            raise json.JSONDecodeError(
                f"Error parsing metadata JSON: {error}"
            ) from error
        except Exception as error:
            raise RuntimeError(
                f"Unexpected error when loading metadata: {error}"
            ) from error

    def check_if_loaded_properly(self, sample: np.ndarray, model: BaseEstimator = None):
        try:
            if model is None:
                model = self.model
                if model is None:
                    raise ValueError("No model provided and no model available.")

            if model and hasattr(model, "predict"):
                random_sample = sample[random.randint(0, sample.shape[0] - 1)]
                prediction = model.predict(random_sample.reshape(1, -1))
                print("Prediction:", prediction)
            else:
                raise ValueError(
                    "Loaded data is not a model or does not have a predict method."
                )
        except Exception as error:
            raise RuntimeError(
                f"Error during model prediction check: {error}"
            ) from error

    def _create_metadata_path(self, model_path: str) -> str:
        """
        Creates a metadata file path for the given model path by replacing
        the model file extension with '.metadata.json'.

        Parameters:
            model_path (str): The path to the model file.

        Returns:
            str: The path to the metadata file.
        """
        if not model_path:
            raise ValueError("Model path must be provided.")

        # Split the model_path into the directory, base filename, and extension
        directory, filename = os.path.split(model_path)
        base_filename, _ = os.path.splitext(filename)

        # Construct the metadata filename and its full path
        metadata_filename = f"{base_filename}.metadata.json"
        metadata_file_path = os.path.join(directory, metadata_filename)

        return metadata_file_path

    def _model_dir_exists(self, model_path_IO: str):
        """
        Checks if the directory for the model file exists.
        """
        model_dir = os.path.dirname(model_path_IO)
        model_dir_exists = os.path.isdir(model_dir)
        return model_dir, model_dir_exists
