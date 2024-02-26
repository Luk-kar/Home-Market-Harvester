# Standard imports
from pathlib import Path
from typing import Any, Dict, Literal
import json
import logging
import os
import pandas as pd

Data_Paths = Dict[str, Any]
Domain = Literal["olx", "otodom", "combined"], "map"

data_timeplace = "2023_11_27_19_41_45_Mierzęcice__Będziński__Śląskie"


class DataPathCleaningManager:
    """
    Manages the paths for cleaned and raw data based on a given time and location.

    This class is responsible for constructing paths for storing and accessing
    cleaned and raw data files, based on a specific time and place identifier.

    Args:
        data_timeplace (str): A string identifier combining time and location.
    """

    def __init__(self, data_timeplace: str, project_root: Path):
        """
        Initialize the DataPathCleaningManager with a specific time and place.

        Args:
            data_timeplace (str): A string identifier combining time and location.
        """
        data_folder = project_root / Path("data")
        self.cleaned_path = Path(data_folder, "cleaned", data_timeplace)
        self.cleaned_path = Path(data_folder, "cleaned", data_timeplace)
        self.raw_path = Path(data_folder, "raw", data_timeplace)

        self.cleaning_stage_path = project_root / "pipeline" / "stages" / "b_cleaning"

        self.paths = {
            "target_folder": self.cleaned_path,
            "olx": {
                "schema": self.cleaned_path / "olx_pl_schema.json",
                "cleaned": self.cleaned_path / "olx.pl.csv",
                "raw": self.raw_path / "olx.pl.csv",
            },
            "otodom": {
                "schema": self.cleaned_path / "otodom_pl_schema.json",
                "cleaned": self.cleaned_path / "otodom.pl.csv",
                "raw": self.raw_path / "otodom.pl.csv",
            },
            "combined": {
                # The schema is preset during the cleaning process to prevent issues
                # in cases where the otodom dataframe might be missing,
                # eliminating the possibility of lacking a reference schema to build upon
                # To develop the combined schema create it in the:
                # notebooks\002_data_cleaning.ipynb.
                # Use the query with the locations with a lot of offers
                # for the best results
                "schema": self.cleaning_stage_path / "combined_df_schema.json",
                "cleaned": self.cleaned_path / "combined.csv",
            },
            "map": {
                "schema": self.cleaned_path / "map_df_schema.json",
                "cleaned": self.cleaned_path / "map_df.csv",
            },
        }

    def save_df(self, df: pd.DataFrame, domain: Domain, save_schema: bool = True):
        """
        Saves a DataFrame to a CSV file in the target folder.

        This method saves the given DataFrame to a CSV file, based on the domain
        specified (e.g., 'olx', 'otodom'). It also ensures the schema file
        is created if it doesn't exist.

        Args:
            df (pd.DataFrame): The DataFrame to be saved.
            domain (str): The domain (e.g., 'olx', 'otodom, combined, map') specifying the folder.
            save_schema (bool): Flag indicating whether to save the schema
                                if it does not exist. Defaults to True.
        """

        target_CSV = self.paths[domain]["cleaned"]

        self._save_dtype_and_index_schema(df, domain)

        df.to_csv(target_CSV, index=False)

        print(f"Saving CSV to {target_CSV}")

    def _save_dtype_and_index_schema(self, df: pd.DataFrame, domain: Domain):
        """
        Saves data types and index information of a DataFrame to a JSON schema file.

        This function creates a schema file that stores the data types and index
        information of the DataFrame, which is useful for ensuring consistency
        when reloading the data.

        Args:
            df (pd.DataFrame): The DataFrame whose schema is to be saved.
        """

        schema_file_path = None
        if domain == "olx":
            schema_file_path = self.paths["olx"]["schema"]
        elif domain == "otodom":
            schema_file_path = self.paths["otodom"]["schema"]
        elif domain == "combined":
            schema_file_path = self.paths["combined"]["schema"]
        elif domain == "map":
            schema_file_path = self.paths["map"]["schema"]
        else:
            message = f"Invalid domain '{domain}' specified."
            raise KeyError(message)

        dtype_info = {str(key): str(value) for key, value in df.dtypes.items()}

        if isinstance(df.index, pd.MultiIndex):
            # Convert multi-level index names and dtypes to string
            index_info = {
                "index_names": [str(name) for name in df.index.names],
                "index_dtypes": [str(dtype) for dtype in df.index.to_series().dtypes],
            }
        else:
            # Convert single-level index name and dtype to string
            index_info = {
                "index_names": str(df.index.name),
                "index_dtypes": str(df.index.to_series().dtype),
            }

        schema_info = {"dtypes": dtype_info, "index": index_info}

        # Ensure the directory exists; if not, create it
        os.makedirs(os.path.dirname(schema_file_path), exist_ok=True)

        with open(schema_file_path, "w") as file:
            json.dump(schema_info, file)

    def load_df(self, domain: Domain, is_cleaned: bool) -> pd.DataFrame:
        """
        Loads the DataFrame from the specified domain.

        Args:
            domain (str): The domain (e.g., 'olx', 'otodom, combined, map') specifying the folder.
            is_cleaned (bool): A boolean indicating whether to load the cleaned or raw DataFrame.

        Returns:
            pd.DataFrame: The DataFrame loaded from the specified CSV file.

        Raises:
            KeyError: If an invalid domain is specified.
        """
        if domain in ["olx", "otodom", "combined", "map"] and is_cleaned:
            return self.load_cleaned_df(domain)
        elif domain in ["olx", "otodom"] and not is_cleaned:
            return self._load_raw_df(domain)
        else:
            message = f"Invalid domain '{domain}' specified."
            raise KeyError(message)

    def _load_raw_df(self, domain: Domain) -> pd.DataFrame:
        data_paths = self.paths

        data_file = data_paths[domain]["raw"]
        df = pd.read_csv(data_file)
        return df

    def load_cleaned_df(self, domain: Domain) -> pd.DataFrame:
        """
        Loads the cleaned DataFrame from the specified domain.

        Args:
            domain (str): The domain (e.g., 'olx', 'otodom, combined, map') specifying the folder.

        Returns:
            pd.DataFrame: The cleaned DataFrame loaded from the specified CSV file.

        Raises:
            KeyError: If an invalid domain is specified.
        """
        data_file = self.paths[domain]["cleaned"]

        # Load the DataFrame from the data file
        if domain in ["olx", "map"]:
            df = pd.read_csv(data_file)
        elif domain in ["otodom", "combined"]:
            df = pd.read_csv(data_file, header=[0, 1])
        else:
            message = f"Invalid domain '{domain}' specified."
            raise KeyError(message)

        # Load the schema information
        schema_info = self.load_schema(domain)

        # Check if the DataFrame columns are a MultiIndex
        if domain in ["olx", "map"]:
            # Apply dtypes for regular index columns
            for col, dtype in schema_info["dtypes"].items():
                col_name = col.strip("()").replace("'", "").replace(", ", "_")
                df[col_name] = df[col_name].astype(dtype)
        elif domain in ["otodom", "combined"]:
            # Apply dtypes for MultiIndex columns
            for col, dtype in schema_info["dtypes"].items():
                col = tuple(col.strip("()").replace("'", "").split(", "))
                df[col] = df[col].astype(dtype)
        else:
            message = f"Invalid domain '{domain}' specified."
            raise KeyError(message)
        return df

    def load_schema(self, domain: Domain) -> Dict:
        """
        Loads the schema information for the specified domain.

        Args:
            domain (str): The domain (e.g., 'olx', 'otodom, combined, map') specifying the folder.

        Returns:
            dict: The schema information for the specified domain.
        """
        schema_file = self.paths[domain]["schema"]

        with open(schema_file, "r") as file:
            schema_info = json.load(file)
        return schema_info
