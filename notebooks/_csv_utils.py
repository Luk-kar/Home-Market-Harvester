from typing import Any
import pandas as pd
import os
import json

Data_Paths = dict[str, Any]

location_and_time = "2023_11_27_19_41_45_Mierzęcice__Będziński__Śląskie"
base_dir = "..\\data"

cleaned_path = f"{base_dir}\\cleaned\\{location_and_time}"
raw_path = f"{base_dir}\\raw\\{location_and_time}"

paths = {
    "target_folder": cleaned_path,
    "olx": {
        "csv": f"{raw_path}\\olx.pl.csv",
        "schema": "olx_pl_schema.json",
        "cleaned": f"{cleaned_path}\\olx.pl.csv",
        "raw": f"{raw_path}\\olx.pl.csv",
    },
    "otodom": {
        "csv": f"{raw_path}\\otodom.pl.csv",
        "schema": "otodom_pl_schema.json",
        "cleaned": f"{cleaned_path}\\otodom.pl.csv",
        "raw": f"{raw_path}\\otodom.pl.csv",
    },
}


def save_df(df: pd.DataFrame, data_paths: Data_Paths, domain: str):
    target_schema = f"{data_paths['target_folder']}\\{data_paths[domain]['schema']}"
    target_CSV = f"{data_paths['target_folder']}\\{data_paths[domain]['csv']}"

    if not os.path.exists(target_schema):
        save_dtype_and_index_schema(df, target_schema)

    if not os.path.exists(target_CSV):
        df.to_csv(target_CSV, index=False)


def save_dtype_and_index_schema(df: pd.DataFrame, schema_file_path: str):
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


def load_df(data_paths: Data_Paths, domain: str) -> pd.DataFrame:
    # Construct the full file paths
    data_file = f"{data_paths['target_folder']}\\{data_paths[domain]['csv']}"
    schema_file = f"{data_paths['target_folder']}\\{data_paths[domain]['schema']}"

    # Load the DataFrame from the data file
    if domain == "olx":
        df = pd.read_csv(data_file)
    elif domain == "otodom":
        df = pd.read_csv(data_file, header=[0, 1])

    # Load the schema information
    with open(schema_file, "r") as file:
        schema_info = json.load(file)

    # Check if the DataFrame columns are a MultiIndex
    if domain == "olx":
        # Apply dtypes for regular index columns
        for col, dtype in schema_info["dtypes"].items():
            col_name = col.strip("()").replace("'", "").replace(", ", "_")
            df[col_name] = df[col_name].astype(dtype)
    elif domain == "otodom":
        # Apply dtypes for MultiIndex columns
        for col, dtype in schema_info["dtypes"].items():
            col = tuple(col.strip("()").replace("'", "").split(", "))
            df[col] = df[col].astype(dtype)
    else:
        raise KeyError(f"Invalid domain '{domain}' specified.")

    return df
