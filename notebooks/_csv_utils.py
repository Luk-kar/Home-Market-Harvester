from typing import Any, Literal
import pandas as pd
import os
import json

Data_Paths = dict[str, Any]
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

    def __init__(self, data_timeplace: str):
        """
        Initialize the DataPathCleaningManager with a specific time and place.

        Args:
            data_timeplace (str): A string identifier combining time and location.
        """
        base_dir = "..\\data"
        self.cleaned_path = f"{base_dir}\\cleaned\\{data_timeplace}"
        self.raw_path = f"{base_dir}\\raw\\{data_timeplace}"

        self.paths = {
            "target_folder": self.cleaned_path,
            "olx": {
                "schema": f"{self.cleaned_path}\\olx_pl_schema.json",
                "cleaned": f"{self.cleaned_path}\\olx.pl.csv",
                "raw": f"{self.raw_path}\\olx.pl.csv",
            },
            "otodom": {
                "schema": f"{self.cleaned_path}\\otodom_pl_schema.json",
                "cleaned": f"{self.cleaned_path}\\otodom.pl.csv",
                "raw": f"{self.raw_path}\\otodom.pl.csv",
            },
            "combined": {
                "schema": f"{self.cleaned_path}\\combined.json",
                "cleaned": f"{self.cleaned_path}\\combined.csv",
            },
            "map": {
                "schema": f"{self.cleaned_path}\\map_df_schema.json",
                "cleaned": f"{self.cleaned_path}\\map_df.csv",
            },
        }

    def save_df(self, df: pd.DataFrame, domain: Domain):
        """
        Saves a DataFrame to a CSV file in the target folder.

        This method saves the given DataFrame to a CSV file, based on the domain
        specified (e.g., 'olx', 'otodom'). It also ensures the schema file
        is created if it doesn't exist.

        Args:
            df (pd.DataFrame): The DataFrame to be saved.
            domain (str): The domain (e.g., 'olx', 'otodom, combined, map') specifying the folder.
        """

        target_schema = self.paths[domain]["schema"]
        target_CSV = self.paths[domain]["cleaned"]

        if not os.path.exists(target_schema):
            self._save_dtype_and_index_schema(df, domain)

        if not os.path.exists(target_CSV):
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
            raise KeyError(f"Invalid domain '{domain}' specified.")

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
        print(f"Saving schema to {schema_file_path}")
        os.makedirs(os.path.dirname(schema_file_path), exist_ok=True)

        with open(schema_file_path, "w") as file:
            json.dump(schema_info, file)

    def load_df(self, domain: Domain, is_cleaned: bool) -> pd.DataFrame:
        """
        Loads a DataFrame from a CSV file in the target folder.
        This method loads a DataFrame from a CSV file, based on the domain
        specified (e.g., 'olx', 'otodom'). It also ensures the schema file
        is created if it doesn't exist.

        Args:
            domain (str): The domain (e.g., 'olx', 'otodom, combined, map') specifying the folder.
            is_cleaned (bool): A boolean specifying whether to load the cleaned or raw data.

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
            raise KeyError(f"Invalid domain '{domain}' specified.")

    def _load_raw_df(self, domain: Domain) -> pd.DataFrame:
        data_paths = self.paths

        data_file = data_paths[domain]["raw"]
        df = pd.read_csv(data_file)
        return df

    def load_cleaned_df(self, domain: Domain) -> pd.DataFrame:
        """
        Loads a cleaned DataFrame from the target folder.

        This method loads a cleaned DataFrame from the target folder, based on the domain
        specified (e.g., 'olx', 'otodom'). It also ensures the schema file
        is created if it doesn't exist.

        Args:
            domain (str): The domain (e.g., 'olx', 'otodom, combined, map') specifying the folder.

        Returns:
            pd.DataFrame: The cleaned DataFrame loaded from the target folder.

        Raises:
            KeyError: If an invalid domain is specified.
        """
        data_file = self.paths[domain]["cleaned"]
        schema_file = self.paths[domain]["schema"]

        # Load the DataFrame from the data file
        if domain in ["olx", "map"]:
            df = pd.read_csv(data_file)
        elif domain in ["otodom", "combined"]:
            df = pd.read_csv(data_file, header=[0, 1])
        else:
            raise KeyError(f"Invalid domain '{domain}' specified.")

            # Load the schema information
        with open(schema_file, "r") as file:
            schema_info = json.load(file)

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
            raise KeyError(f"Invalid domain '{domain}' specified.")
        return df
