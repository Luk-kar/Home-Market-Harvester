"""
This module provides a comprehensive pipeline for processing and analyzing property data, 
aimed at preparing the data for machine learning modeling, specifically linear regression analysis. 
The pipeline includes functions for setting the project root directory, loading cleaned data, 
filtering rows based on predefined criteria, preprocessing features 
(including creating dummy variables and imputing missing values), 
and training a linear regression model to predict property prices.
"""

# python pipeline/stages/c_model_developing/model_training.py

# Standard library imports
from datetime import datetime
from pathlib import Path
import sys
from typing import Tuple

# Third party imports
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.impute import KNNImputer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


def set_project_root() -> Path:
    """
    Sets the project root and appends it to the system path.

    Returns:
        Path: The root directory of the project.
    """
    project_root = Path(__file__).resolve().parents[3]
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))
    return project_root


set_project_root()

# Local imports
from pipeline.components.logging import setup_logging, log_and_print
from pipeline.config._conf_file_manager import ConfigManager
from pipeline.stages._csv_utils import DataPathCleaningManager
from pipeline.stages.c_model_developing.model_io_operations import ModelManager


def load_data(project_root: str, data_timeplace: str) -> pd.DataFrame:
    """
    Load and return the cleaned data for model training.

    Parameters:
    project_root (str): The root directory of the project.

    Returns:
    pd.DataFrame: The cleaned data for model training.
    """

    data_path_manager = DataPathCleaningManager(data_timeplace, project_root)
    df = data_path_manager.load_cleaned_df(domain="combined")

    return df


def get_current_scraped_folder_name() -> str:
    """
    Get the current scraped folder name from the configuration file.

    Returns:
    str: The current scraped folder name.
    """

    config_file = ConfigManager("run_pipeline.conf")
    TIMEPLACE = "MARKET_OFFERS_TIMEPLACE"
    data_timeplace = config_file.read_value(TIMEPLACE)

    if data_timeplace is None:
        raise ValueError(f"The configuration variable {TIMEPLACE} is not set.")
    return data_timeplace


def filter_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filters the DataFrame to include only relevant rows for modeling.

    Args:
        df (pd.DataFrame): The DataFrame containing the data to filter.

    Returns:
        pd.DataFrame: A new DataFrame containing only the relevant rows.
    """
    return df[df.apply(filter_relevant_rows, axis=1)].copy()


def filter_relevant_rows(row: pd.Series) -> bool:
    """
    Determines whether a row meets specific conditions
    related to property location and characteristics.

    Args:
        row (pd.Series): A row from a DataFrame representing property data.

    Returns:
        bool: True if the row meets the conditions; otherwise, False.
    """

    cities_to_exclude = [
        "Katowice",
        "Sosnowiec",
        "Bytom",
        "Dąbrowa Górnicza",
        "Chorzów",
        "Jaworzno",
        "Mysłowice",
        "Świętochłowice",
        "Ruda Śląska",
        "częstochowski",
        "Mikołów",
        "Ogrodzieniec",
        "Olkusz",
        "Będzin",
        "Czeladź",
        "Zabrze",
        "Częstochowa",
        "Tychy",
    ]

    building_types_to_include = ["block_of_flats", "apartment_building"]

    prices_up_to = 4000

    if pd.isna(row["location"]["city"]):
        raise ValueError(
            "Unexpected NA value found in 'city'. Row data may be incomplete or corrupted."
        )

    if pd.isna(row["pricing"]["total_rent"]):
        raise ValueError(
            "Unexpected NA value found in 'total_rent'. Row data may be incomplete or corrupted."
        )

    city = row["location"]["city"]
    building_type = row["type_and_year"]["building_type"]
    total_rent = row["pricing"]["total_rent"]

    city_condition = city not in cities_to_exclude
    building_type_condition = (
        not pd.isna(building_type) and building_type in building_types_to_include
    )
    price_condition = total_rent <= prices_up_to

    return city_condition and building_type_condition and price_condition


def calculate_building_age(build_years: pd.Series) -> pd.Series:
    """
    Calculates the age of buildings from a series of build years.

    Args:
        build_years (pd.Series): A pandas Series containing the year each building was constructed.

    Returns:
        pd.Series: A pandas Series containing the calculated age of each building.
    """
    current_year = datetime.now().year
    return build_years.apply(lambda x: current_year - x if pd.notna(x) else np.nan)


def preprocess_features(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, np.ndarray]:
    """
    Preprocesses DataFrame features for modeling,
    including dummy variable creation and missing value imputation.

    Args:
        df (pd.DataFrame): The DataFrame containing the data to model.

    Returns:
        Tuple[pd.DataFrame, np.ndarray]:
            A tuple containing the processed feature matrix (X) and target array (Y),

    Raises:
        ValueError: If all values are missing in any column after preprocessing.
    """

    df_model = select_columns_for_modeling(df)

    df_dum = pd.get_dummies(df_model)

    X = df_dum.drop("total_rent_sqm", axis=1)

    Y = df_dum["total_rent_sqm"].replace([np.inf, -np.inf], np.nan).fillna(0)

    bool_cols = X.select_dtypes(include=["bool"]).columns
    X[bool_cols] = X[bool_cols].astype(int)
    X = X.replace([np.inf, -np.inf], np.nan)

    if X.isnull().all().any():
        missing_data_columns = X.columns[X.isnull().all()].tolist()
        raise ValueError(
            "All values are missing in the following columns,"
            f" which makes them unsuitable for training:\n{missing_data_columns}\n"
        )

    X["build_year"] = calculate_building_age(X["build_year"]).values

    knn_imputer = KNNImputer(n_neighbors=5)
    X_imputed = knn_imputer.fit_transform(X).astype(float)
    X_imputed_df = pd.DataFrame(X_imputed, columns=X.columns)

    return X_imputed_df, Y.values


def select_columns_for_modeling(df: pd.DataFrame) -> pd.DataFrame:
    """
    Selects and preprocesses a subset of columns from the DataFrame for modeling.

    Args:
        df (pd.DataFrame): The original DataFrame from which to select columns.

    Returns:
        pd.DataFrame: A DataFrame with selected and potentially transformed columns for modeling.
    """
    columns_to_select = [
        ("pricing", "total_rent_sqm"),
        ("size", "square_meters"),
        ("type_and_year", "build_year"),
        ("equipment", "dishwasher"),
    ]
    extracted_columns_df = df.loc[:, columns_to_select]

    extracted_columns_df.columns = drop_multi_level_indexing(
        extracted_columns_df.columns
    )
    return extracted_columns_df


def drop_multi_level_indexing(columns: pd.MultiIndex) -> pd.Index:
    """
    Drops the top level of a multi-level index in a pandas MultiIndex object,
    simplifying it to a single-level Index.

    Args:
        columns (pd.MultiIndex): A pandas MultiIndex object from a DataFrame.

    Returns:
        pd.Index: A pandas Index object with the top level removed.

    Raises:
        ValueError: If the provided 'columns' object is not a MultiIndex with exactly two levels.
    """

    if not isinstance(columns, pd.MultiIndex) or columns.nlevels != 2:
        raise ValueError(
            "The 'columns' parameter must be a MultiIndex with exactly two levels."
        )
    return columns.droplevel(0)


def train_model(X_train: pd.DataFrame, Y_train: np.ndarray) -> LinearRegression:
    """
    Trains a linear regression model using the provided training feature set and target values.

    Args:
        X_train (pd.DataFrame): The feature matrix as a pandas DataFrame
                                with shape (n_samples, n_features).
        Y_train (np.ndarray): The target values as a NumPy array with shape (n_samples,).

    Returns:
        LinearRegression: A trained linear regression model.
    """

    feature_names = (
        X_train.columns.tolist() if isinstance(X_train, pd.DataFrame) else None
    )

    if not feature_names:
        raise ValueError(
            "The feature names could not be determined.\n"
            "The feature matrix must be a DataFrame."
        )

    # Look at `004_model_building.ipynb` the reasons for using LinearRegression
    model = LinearRegression().fit(X_train, Y_train)

    log_and_print(
        (
            f"Model of type {type(model).__name__} trained successfully.\n"
            f"Model trained with feature names: {feature_names}.\n"
            f"Trained on {X_train.shape[0]} samples."
        )
    )

    return model


def save_model(project_root: Path, data_timeplace, model, X_train):
    """
    Saves the trained model along with its training data to disk.

    Args:
        project_root (Path):   The root directory of the project as a Path object.
                               This is where the model directory will be created.

        data_timeplace (str):  A string identifier for the specific model version
                               or training instance.
                               This is used to create a unique directory for saving the model.

        model (BaseEstimator): The trained model object.
                               This can be any estimator following
                               the scikit-learn estimator interface.

        X_train (pd.Dataframe): The training data used to train the model.


    Returns:
        None
    """

    models_dir_path = project_root / "model" / data_timeplace
    models_dir_path.mkdir(parents=True, exist_ok=True)
    model_path = str(models_dir_path / "model.pkl")
    model_manager = ModelManager(
        model_path=model_path, model=model, training_data=X_train
    )
    model_manager.save_model_and_metadata()


def validate_model(
    X_test: pd.DataFrame, Y_test: np.ndarray, model: BaseEstimator
) -> None:
    """
    Validates the trained model by predicting on the test set and calculating the mean error.

    The function predicts the target values using the model and the test feature set,
    then computes the mean absolute error between the predicted and actual target values
    in the test set. This error is logged to provide an insight into the model's performance.

    Args:
        X_test (pd.DataFrame): The test feature set as a pandas DataFrame.
        Y_test (np.ndarray): The actual target values for the test set as a NumPy array.
        model (BaseEstimator): The trained model to be validated.

    Raises:
        ValueError: If the input data does not match expected dimensions or types.
        RuntimeError: If the model prediction fails due to unexpected issues.
    """

    if not isinstance(X_test, pd.DataFrame):
        raise ValueError("X_test must be a pandas DataFrame.")
    if not isinstance(Y_test, np.ndarray):
        raise ValueError("Y_test must be a NumPy array.")

    try:
        Y_pred = model.predict(X_test)
    except Exception as e:
        raise RuntimeError(f"Model prediction failed: {e}")

    # The mean absolute error between actual and predicted values
    model_accuracy_error = np.mean(np.abs(Y_test - Y_pred))

    log_and_print(f"Mean error of the model: {model_accuracy_error:.2f}")


def main():
    """
    Main function to execute the model training and saving workflow.
    """

    setup_logging()

    project_root = set_project_root()
    data_timeplace = get_current_scraped_folder_name()

    df = load_data(project_root, data_timeplace)

    df_filtered = filter_data(df)
    X, Y = preprocess_features(df_filtered)
    X_train, X_test, Y_train, Y_test = train_test_split(
        X, Y, test_size=0.2, random_state=42
    )

    model = train_model(X_train, Y_train)

    validate_model(X_test, Y_test, model)

    save_model(project_root, data_timeplace, model, X)


if __name__ == "__main__":
    main()
