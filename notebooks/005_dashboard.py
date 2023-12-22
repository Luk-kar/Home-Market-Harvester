# Srandard imports
import os

# Third party imports
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

# Local imports
from _csv_utils import data_timeplace, DataPathCleaningManager


def set_plot_aesthetics(
    ax,
    title=None,
    xlabel=None,
    ylabel=None,
    title_color="#435672",
    tick_color="#435672",
    fontweight="bold",
):
    if title:
        ax.set_title(title, color=title_color, fontweight=fontweight)
    if xlabel:
        ax.set_xlabel(xlabel, fontweight=fontweight)
    if ylabel:
        ax.set_ylabel(ylabel, fontweight=fontweight)
    ax.tick_params(colors=tick_color, which="both")  # For both major and minor ticks
    ax.yaxis.label.set_color(tick_color)  # Y-axis label color
    ax.xaxis.label.set_color(tick_color)  # X-axis label color

    sns.despine(right=True, top=True)

    for spine in ax.spines.values():  # Spine color
        spine.set_edgecolor(tick_color)


def plot_bar_chart(data, title):
    # Convert the data dictionary to a DataFrame for Seaborn
    df = pd.DataFrame(list(data.items()), columns=["Category", "Price"])

    # Create the bar plot using Seaborn
    fig, ax = plt.subplots()
    sns.barplot(x="Category", y="Price", data=df, ax=ax)

    set_plot_aesthetics(ax, title=title, xlabel="Category", ylabel="Price")

    return fig


def render_dashboard(data, plot_bar_chart):
    your_offers_df, other_offers_df, map_offers_df = data

    text = "Rent comparisons"
    st.markdown(
        f"<h1 style='text-align: center; font-style: italic;'>{text}</h1>",
        unsafe_allow_html=True,
    )
    text = "yours vs market"
    st.markdown(
        f"<h3 style='text-align: center; font-style: italic;'>{text}</h3>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        unfurnished_data = {"per meter": 1000, "per apartment": 20000}
        st.pyplot(plot_bar_chart(unfurnished_data, "Unfurnished"))

    with col2:
        furnished_data = {"per meter": 1200, "per apartment": 24000}
        st.pyplot(plot_bar_chart(furnished_data, "Furnished"))

    st.table(data)


def get_absolute_path(relative_path):
    current_dir = os.getcwd()
    absolute_path = os.path.join(current_dir, relative_path)
    normalized_path = os.path.normpath(absolute_path)

    return normalized_path


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


# Mock data
# data = pd.DataFrame(
#     {
#         "flat": [1, 2, 3],
#         "floor": [1, 2, 3],
#         "furnished": [True, False, True],
#         "price per meter": [1000, 1100, 1000],
#         "area": [20, 14, 20],
#     }
# )

data = upload_data()

render_dashboard(data, plot_bar_chart)

# Display additional tables or charts as necessary

# Run this from your command line:
# streamlit run your_script_name.py
