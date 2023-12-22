import pandas as pd
import os

# Local imports
from _csv_utils import data_timeplace, DataPathCleaningManager


def update_paths_recursively(d: dict, old_str: str, new_str: str) -> None:
    """
    Recursively updates all string values in a nested dictionary.

    This function traverses through each item in the provided dictionary. If it encounters a string, it replaces
    occurrences of 'old_str' with 'new_str'. If it encounters another dictionary, it recursively applies the same
    process to that dictionary.

    Parameters:
    d (dict): The dictionary to be updated. It can be nested with other dictionaries.
    old_str (str): The string to be replaced.
    new_str (str): The string to replace with.

    Returns:
    None: The function modifies the dictionary in place and does not return anything.
    """

    for key, value in d.items():
        if isinstance(value, dict):
            update_paths_recursively(value, old_str, new_str)
        else:
            d[key] = value.replace(old_str, new_str)


def upload_data():
    data_path_manager = DataPathCleaningManager(data_timeplace)

    update_paths_recursively(data_path_manager.paths, "..\\data", "data")

    your_offers_df = pd.read_csv("../to_compare_example_data.csv")
    other_offers_df = data_path_manager._load_cleaned_df(domain="combined")
    map_offers_df = data_path_manager.load_df("map", is_cleaned=True)

    return your_offers_df, other_offers_df, map_offers_df


your_offers_df, other_offers_df, map_offers_df = upload_data()

print("Your offers:")
print(map_offers_df.head())
