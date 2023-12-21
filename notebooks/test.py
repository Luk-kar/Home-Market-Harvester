import pandas as pd
import os


def get_absolute_path(relative_path):
    # Get the current working directory
    current_dir = os.getcwd()
    # Join the current directory with the relative path
    absolute_path = os.path.join(current_dir, relative_path)
    # Normalize the path (collapsing any ../ parts)
    absolute_path = os.path.normpath(absolute_path)
    return absolute_path


path = "../to_compare_example_data.csv"
abs_path = get_absolute_path(path)

your_offers_df = pd.read_csv("../to_compare_example_data.csv")

print(your_offers_df)
