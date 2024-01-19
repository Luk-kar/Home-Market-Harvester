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

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model_metadata_file_path = self._create_metadata_path(model_path)

    def save_dataframe_metadata(self, df: pd.DataFrame):
        try:
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

    def save_model(self, model: BaseEstimator):
        try:
            pickl = {"model": model}
            with open(self.model_path, "wb") as file:
                pickle.dump(pickl, file)
        except IOError as error:
            raise IOError(f"Error saving model: {error}") from error
        except Exception as error:
            raise RuntimeError(
                f"Unexpected error when saving model: {error}"
            ) from error

    def load_model(self) -> BaseEstimator:
        try:
            with open(self.model_path, "rb") as pickled:
                data = pickle.load(pickled)
                return data.get("model")
        except FileNotFoundError as error:
            raise FileNotFoundError(
                f"Model file not found at {self.model_path}"
            ) from error
        except pickle.UnpicklingError as error:
            raise pickle.UnpicklingError(f"Error loading model: {error}") from error
        except Exception as error:
            raise RuntimeError(
                f"Unexpected error when loading model: {error}"
            ) from error

    def check_if_loaded_properly(self, sample: np.ndarray):
        try:
            model = self.load_model()

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
