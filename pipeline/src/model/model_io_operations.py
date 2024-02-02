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

    Args:
        model_path (str): The path to the model file.
        model (BaseEstimator, optional): The machine learning model to be saved.
                                            If None, the class's model attribute is used.
        training_data (pd.DataFrame, optional): The DataFrame whose metadata is to be saved.
    """

    def __init__(
        self,
        model_path: str,
        model: BaseEstimator = None,
        training_data: pd.DataFrame = None,
    ):
        # Check if the directory exists
        model_dir_exists = self._model_dir_exists(model_path)
        if not model_dir_exists:
            raise FileNotFoundError(f"The directory {model_path} does not exist.")

        self.model_path = model_path
        self.model = model
        self.model_metadata_path = self._create_metadata_path(model_path)
        self.training_data = training_data

    def save_model_and_metadata(
        self,
        model: BaseEstimator = None,
        model_path: str = None,
        df: pd.DataFrame = None,
    ):
        """
        Saves both the machine learning model and the DataFrame metadata.

        This method is a convenience function for saving the specified machine learning model
        to a file and saving the metadata of a provided DataFrame to a JSON file. The metadata
        includes information such as column names, data types, and column order. If either the
        model, model path, or DataFrame is not provided, the method falls back to using the
        respective attributes stored in the class instance.

        Args:
            model (BaseEstimator, optional): The machine learning model to be saved.
                                             If None, the class's model attribute is used.
            model_path (str, optional): The file path where the model will be saved.
                                        If None, the class's model_path attribute is used.
            df (pd.DataFrame, optional): The DataFrame whose metadata is to be saved.
                                         If None, the class's training_data attribute is used.

        Raises:
            ValueError: If no model, model path, or DataFrame is provided and no corresponding
                        attribute is available in the instance.
        """

        df = self._get_attribute_or_raise(df, self.training_data, "DataFrame")
        model = self._get_attribute_or_raise(model, self.model, "model")
        model_path = self._get_attribute_or_raise(
            model_path, self.model_path, "model path"
        )

        self.save_dataframe_metadata(df)
        self.save_model(model, model_path)

    def load_model_and_metadata(
        self, model_path: str = None, model_metadata_path: str = None
    ) -> (BaseEstimator, dict):
        """
        Loads the model and its metadata from specified file paths.

        If the file paths are not provided, it defaults to the paths stored in the class instance.
        The method raises a ValueError if the paths are not available
        either as arguments or in the instance.

        Args:
            model_path (str, optional): The file path where the model is saved.
                                        If None, uses the class's model_path attribute.
            model_metadata_path (str, optional): The file path where the metadata is saved.
                                                 If None, uses the class's
                                                 model_metadata_file_path attribute.

        Returns:
            tuple: A tuple containing the loaded machine learning model
            and its metadata as a dictionary.

        Raises:
            ValueError: If no model path or metadata file path is provided
            and none are available in the instance.
        """

        model_path = self._validate_path(model_path or self.model_path, "Model path")
        model_metadata_path = self._validate_path(
            model_metadata_path or self.model_metadata_path, "Model metadata path"
        )

        model = self.load_model(model_path)
        metadata = self.load_metadata(model_metadata_path)
        return model, metadata

    def save_model(self, model: BaseEstimator = None, model_path: str = None):
        """
        Saves a machine learning model to the specified file path.

        This method allows saving a provided machine learning model to a given file path.
        If either the model or the model path is not provided,
        the method falls back to using the respective
        attributes stored in the class instance.

        Parameters:
            model (BaseEstimator, optional): The machine learning model to be saved.
                                            If None, the class's model attribute is used.
            model_path (str, optional): The file path where the model will be saved.
                                        If None, the class's model_path attribute is used.

        Raises:
            ValueError: If no model is provided and no model is available in the instance,
                        or if no model path is provided
                        and no model path is available in the instance.
            IOError: If there is an error in saving the model file.
            RuntimeError: If an unexpected error occurs during the model saving process.
        """

        model = self._get_attribute_or_raise(model, self.model, "model")
        model_path = self._get_attribute_or_raise(
            model_path, self.model_path, "model path"
        )

        try:
            pickl = {"model": model}
            with open(model_path, "wb") as file:
                pickle.dump(pickl, file)
        except IOError as error:
            raise IOError(f"Error saving model: {error}") from error
        except Exception as error:
            raise RuntimeError(
                f"Unexpected error when saving model: {error}"
            ) from error

    def save_dataframe_metadata(self, df: pd.DataFrame = None, model_path: str = None):
        """
        Saves metadata of a DataFrame to a JSON file.

        The metadata includes column names, data types, and column order, which is useful
        for ensuring consistency in data used for training and predictions. If a specific
        model path is provided, the metadata file is created in accordance with that path;
        otherwise, it uses the default model metadata file path set in the class.

        Args:
            df (pd.DataFrame, optional): The DataFrame whose metadata is to be saved.
                                         If not provided, the class's training_data is used.
            model_path (str, optional): The file path to save the metadata.
                                        If not provided,
                                        uses the class's model_metadata_file_path attribute.

        Raises:
            ValueError: If no DataFrame is provided
                        and no training data is available in the instance,
                        or if no metadata file path is provided
                        and no model path is available in the instance.
            IOError: If there is an error in saving the metadata file.
            RuntimeError: If an unexpected error occurs during the metadata file saving process.
        """

        try:
            df = self._get_attribute_or_raise(df, self.training_data, "DataFrame")
            metadata_file_path = self._get_metadata_file_path(model_path)

            metadata = {
                "columns": {col: str(df[col].dtype) for col in df.columns},
                "column_order": list(df.columns),
            }

            with open(metadata_file_path, "w", encoding="utf-8") as file:
                json.dump(metadata, file, indent=4)
        except IOError as error:
            raise IOError(f"Error saving DataFrame metadata: {error}") from error
        except Exception as error:
            raise RuntimeError(
                f"Unexpected error when saving DataFrame metadata: {error}"
            ) from error

    def load_model(self, model_path) -> BaseEstimator:
        """
        Loads a machine learning model from the specified file path.

        If the file path is not provided, it defaults to the path stored in the class instance.
        The method raises a ValueError if the path is not available
        either as an argument or in the instance.

        Args:
            model_path (str, optional): The file path where the model is saved.
                                        If None, uses the class's model_path attribute.

        Returns:
            BaseEstimator: The loaded machine learning model.

        Raises:
            ValueError: If no model path is provided and none is available in the instance.
            FileNotFoundError: If the specified model file does not exist.
            pickle.UnpicklingError: If there is an error in unpickling the model file.
            RuntimeError: If an unexpected error occurs during the model loading process.
        """

        model_path = self._validate_path(model_path or self.model_path, "Model path")

        try:
            with open(model_path, "rb") as pickled:
                data = pickle.load(pickled)
                return data.get("model")
        except FileNotFoundError as error:
            raise FileNotFoundError(f"Model file not found at {model_path}") from error
        except pickle.UnpicklingError as error:
            raise pickle.UnpicklingError(f"Error loading model: {error}") from error
        except Exception as error:
            raise RuntimeError(
                f"Unexpected error when loading model: {error}"
            ) from error

    def load_metadata(self, model_metadata_file_path: str = None) -> dict:
        """
        Loads metadata for a DataFrame from a specified JSON file for a model feed.

        If the file path is not provided, it defaults to the path stored in the class instance.
        The method raises a ValueError if the path is not available
        either as an argument or in the instance.

        Args:
            model_metadata_file_path (str, optional): The file path where the metadata is saved.
                                                      If None,
                                                      uses the class's model_metadata_file_path attribute.

        Returns:
            dict: The loaded metadata, which may include column names, data types, and column order.

        Raises:
            ValueError: If no metadata file path is provided and none is available in the instance.
            FileNotFoundError: If the specified metadata file does not exist.
            json.JSONDecodeError: If there is an error in parsing the metadata JSON file.
            RuntimeError: If an unexpected error occurs during the metadata loading process.
        """

        model_metadata_file_path = self._validate_path(
            model_metadata_file_path or self.model_metadata_path,
            "Model metadata file path",
        )

        try:
            with open(model_metadata_file_path, "r", encoding="utf-8") as file:
                max_metadata_size = 10 * 1024 * 1024  # 10 MB size limit
                if file.tell() >= max_metadata_size:
                    raise ValueError(
                        "Metadata file size exceeded limit of 10 MB."
                        + f"metadata_file_path:\n{model_metadata_file_path}"
                        + f"metadata_file_size:\n{file.tell()}"
                    )
                return json.load(file)
        except FileNotFoundError as error:
            raise FileNotFoundError(
                f"Metadata file not found at {self.model_metadata_path}"
            ) from error
        except json.JSONDecodeError as error:
            error_msg = (
                f"Error parsing metadata JSON at {model_metadata_file_path}: {error}"
            )
            raise json.JSONDecodeError(error_msg, error.doc, error.pos) from error
        except Exception as error:
            raise RuntimeError(
                f"Unexpected error when loading metadata: {error}"
            ) from error

    def evaluate_model_on_sample(self, sample: np.ndarray, model: BaseEstimator = None):
        """
        Checks if the provided or stored model can make predictions on a sample.

        This method tests the model's predict method on a random sample
        from the provided array to verify if the model is loaded properly
        and can make predictions.
        If the model is not provided,
        it falls back to using the model stored in the class instance.

        Parameters:
            sample (np.ndarray): An array of sample data for testing the model.
            model (BaseEstimator, optional): The machine learning model to be tested.
                                            If None, the class's model attribute is used.

        Raises:
            ValueError: If the model is not provided or available,
                        or if it lacks a predict method.
            RuntimeError: If an error occurs during the prediction check process.

        Note:
            This function prints the prediction result for the randomly selected sample.
        """
        try:
            model = self._get_attribute_or_raise(model, self.model, "model")

            if model is None:
                raise ValueError("No model is available for prediction.")

            if not hasattr(model, "predict"):
                raise ValueError("The provided model does not have a 'predict' method.")

            random_sample = sample[random.randint(0, sample.shape[0] - 1)]
            prediction = model.predict(random_sample.reshape(1, -1))
            print("Prediction:", prediction)

        except Exception as error:
            raise RuntimeError(
                f"Error during model prediction check: {error}"
            ) from error

    def _create_metadata_path(self, model_path: str) -> str:
        """
        Creates a metadata file path for the given model path by replacing
        the model file extension with '.metadata.json'.

        Args:
            model_path (str): The path to the model file.

        Returns:
            str: The path to the metadata file.
        """
        if not model_path:
            raise ValueError(
                "Model path must be provided.\n" + f"model_path:\n{model_path}"
            )

        # Split the model_path into the directory, base filename, and extension
        directory, filename = os.path.split(model_path)
        base_filename, _ = os.path.splitext(filename)

        # Construct the metadata filename and its full path
        metadata_filename = f"{base_filename}.metadata.json"
        metadata_file_path = os.path.join(directory, metadata_filename)

        return metadata_file_path

    def _model_dir_exists(self, model_path: str) -> bool:
        """
        Checks if the directory for the model file exists.

        Args:
            model_path (str): The path to the model file.

        Returns:
            bool: True if the directory exists, False otherwise.
        """
        model_dir = os.path.dirname(model_path)
        model_dir_exists = os.path.isdir(model_dir)
        return model_dir_exists

    def _validate_path(self, path: str, path_kind: str) -> str:
        """
        Validates a file path.

        Args:
            path (str): The file path to validate.
            path_kind (str): The name of the path (for error messages).

        Returns:
            str: The validated file path.

        Raises:
            ValueError: If the path is None or does not exist.
        """
        if path is None:
            raise ValueError(
                f"No {path_kind} provided and no {path_kind} available in the instance."
            )

        if not os.path.exists(path):
            raise FileNotFoundError(f"{path_kind} not found at {path}")

        return path

    def _get_attribute_or_raise(self, value, attribute, attribute_name: str):
        """
        Gets the value of an attribute or raises a ValueError
        if both the value and the attribute are None.

        Parameters:
            value: The value to check.
            attribute: The class attribute to fall back to if the value is None.
            attribute_name (str): The name of the attribute for the error message.

        Returns:
            The value or the class attribute.

        Raises:
            ValueError: If both the value and the attribute are None.
        """
        if value is None:
            if attribute is None:
                raise ValueError(
                    f"No {attribute_name} provided"
                    + f" and no {attribute_name} available in the instance."
                )
            return attribute
        return value

    def _get_metadata_file_path(self, model_path: str = None) -> str:
        """
        Determines the metadata file path based on the provided model path.

        If a specific model path is provided, it creates a metadata file path accordingly.
        Otherwise, it uses the default metadata file path set in the class.

        Parameters:
            model_path (str, optional): The custom file path for the model.

        Returns:
            str: The determined file path for the metadata.

        Raises:
            ValueError: If the model path is provided but invalid for creating a metadata file path.
        """
        if model_path is not None:
            metadata_file_path = self._create_metadata_path(model_path)
            if not metadata_file_path:
                raise ValueError(
                    "Model path must be provided to create metadata file path.\n"
                    + f"model_path:\n{model_path}"
                )
            return metadata_file_path
        else:
            return self.model_metadata_path
