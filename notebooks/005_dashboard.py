# Srandard imports
import os

# Third party imports
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
import matplotlib.colors as mcolors

# Local imports
from _csv_utils import data_timeplace, DataPathCleaningManager

aesthetics_plots = {
    "title_size": 16,
    "y_and_x_label_size": 12,
    "fontweight": "bold",
    "label_color": "#435672",
    "palette": "viridis",
    "figsize": {
        "multiplot": (15, 10),  # (width, height) in inches
        "singleplot": (8, 6),
    },
}


def get_darker_shade(color: str, factor=0.5) -> str:
    rgb = mcolors.hex2color(color)
    darkened_rgb = [max(0, c * factor) for c in rgb]
    darkened_hex = mcolors.rgb2hex(darkened_rgb)

    return darkened_hex


def set_plot_aesthetics(
    ax,
    data_series,
    title=None,
    xlabel=None,
    ylabel=None,
    title_color=aesthetics_plots["label_color"],
    tick_color=aesthetics_plots["label_color"],
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

    # Add annotations for each bar
    for p in ax.patches:
        _value = p.get_height()
        # Place the annotation above the bar
        if _value > 0:
            ax.annotate(
                _value,
                (p.get_x() + p.get_width() / 2.0, p.get_height()),
                ha="center",
                va="bottom",
                fontsize=10,
                weight=aesthetics_plots["fontweight"],
                color=aesthetics_plots["label_color"],
                xytext=(0, 2),
                textcoords="offset points",
            )

    my_palette = [
        "#bfed2d",
        get_darker_shade("#bfed2d"),
        "#007e90",
        get_darker_shade("#007e90"),
        "#FF9F66",
        get_darker_shade("#FF9F66"),
    ]

    # Set the color of each bar
    for index, p in enumerate(ax.patches):
        color_index = index % len(my_palette)  # Ensure the index loops over my_palette
        p.set_color(my_palette[color_index])


def plot_bar_chart(data, title, xlabel, ylabel):
    # Convert the data dictionary to a DataFrame for Seaborn
    df = pd.DataFrame(list(data.items()), columns=["Category", "Price"])

    # Create the bar plot using Seaborn
    fig, ax = plt.subplots(figsize=aesthetics_plots["figsize"]["multiplot"])
    sns.barplot(x="Category", y="Price", data=df, ax=ax, palette="viridis")

    set_plot_aesthetics(ax, df["Price"], title=title, xlabel=xlabel, ylabel=ylabel)

    return fig


def render_dashboard(data):
    st.set_page_config(layout="wide")

    display_title()

    your_offers_df, other_offers_df, map_offers_df = data

    display_bar_charts(plot_bar_chart, your_offers_df, other_offers_df)

    # Display the table
    st.table(data)


def display_title():
    text = "🔍🏠 Rent comparisons"
    st.markdown(
        f"<h1 style='text-align: center;'>{text}</h1>",
        unsafe_allow_html=True,
    )


def display_bar_charts(plot_bar_chart, your_offers_df, other_offers_df):
    text = "median price"
    st.markdown(
        f"<h3 style='text-align: center; font-style: italic;'>{text}</h3>",
        unsafe_allow_html=True,
    )

    offers = {
        "yours": {
            "furnished": your_offers_df[your_offers_df["is_furnished"] == True],
            "unfurnished": your_offers_df[your_offers_df["is_furnished"] == False],
        },
        "local": {
            "furnished": other_offers_df[
                (other_offers_df["equipment"]["furniture"] == True)
                & (other_offers_df["location"]["city"] == "będziński")
            ],
            "unfurnished": other_offers_df[
                (other_offers_df["equipment"]["furniture"] == False)
                & (other_offers_df["location"]["city"] == "będziński")
            ],
        },
        "20 km radius": {
            "furnished": other_offers_df[
                other_offers_df["equipment"]["furniture"] == True
            ],
            "unfurnished": other_offers_df[
                other_offers_df["equipment"]["furniture"] == False
            ],
        },
    }

    col_per_meter, col_per_offer = st.columns(2)

    space = " " * 62
    categories = ["Yours", "Local", "20 km radius"]

    max_length = max(len(category) for category in categories)
    centered_categories = [category.center(max_length) for category in categories]

    xlabel = space.join(centered_categories)

    with col_per_meter:
        per_meter_data = {
            "furnished ": offers["yours"]["furnished"]["price_per_meter"].median(),
            "unfurnished ": offers["yours"]["unfurnished"]["price_per_meter"].median(),
            "furnished": round(
                offers["local"]["furnished"]["pricing"]["total_rent_sqm"].median(), 2
            ),
            "unfurnished": round(
                offers["local"]["unfurnished"]["pricing"]["total_rent_sqm"].median(),
                2,
            ),
            " furnished": round(
                offers["20 km radius"]["furnished"]["pricing"][
                    "total_rent_sqm"
                ].median(),
                2,
            ),
            " unfurnished": round(
                offers["20 km radius"]["unfurnished"]["pricing"][
                    "total_rent_sqm"
                ].median(),
                2,
            ),
        }
        st.pyplot(
            plot_bar_chart(
                per_meter_data,
                "Price per meter",
                xlabel,
                "Price",
            )
        )

    with col_per_offer:
        per_offer_data = {
            "furnished ": offers["yours"]["furnished"]["price"].median(),
            "unfurnished ": offers["yours"]["unfurnished"]["price"].median(),
            "furnished": round(
                offers["local"]["furnished"]["pricing"]["total_rent"].median(), 2
            ),
            "unfurnished": round(
                offers["local"]["unfurnished"]["pricing"]["total_rent"].median(),
                2,
            ),
            " furnished": round(
                offers["20 km radius"]["furnished"]["pricing"]["total_rent"].median(), 2
            ),
            " unfurnished": round(
                offers["20 km radius"]["unfurnished"]["pricing"]["total_rent"].median(),
                2,
            ),
        }
        st.pyplot(
            plot_bar_chart(
                per_offer_data,
                "Price per offer",
                xlabel,
                "Price",
            )
        )


def get_absolute_path(relative_path):
    current_dir = os.getcwd()
    absolute_path = os.path.join(current_dir, relative_path)
    normalized_path = os.path.normpath(absolute_path)

    return normalized_path


def update_paths(d: dict, old_str: str, new_str: str) -> None:
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
            update_paths(value, old_str, new_str)
        else:
            d[key] = value.replace(old_str, new_str)


def upload_data():
    data_path_manager = DataPathCleaningManager(data_timeplace)

    update_paths(data_path_manager.paths, "..\\data", "data")

    your_offers_df = pd.read_csv("../to_compare_example_data.csv")

    your_offers_df["flat_id"] = your_offers_df["flat_id"].astype("Int64")
    your_offers_df["floor"] = your_offers_df["floor"].astype("Int64")
    your_offers_df["area"] = your_offers_df["area"].astype("Float64")
    your_offers_df["is_furnished_o"] = your_offers_df["is_furnished"]
    your_offers_df["is_furnished"] = your_offers_df["is_furnished"].astype("bool")
    your_offers_df["price"] = your_offers_df["price"].astype("Float64")
    your_offers_df["price_per_meter"] = your_offers_df.apply(
        lambda row: round(row["price"] / row["area"], 2)
        if pd.notna(row["price"]) and pd.notna(row["area"])
        else np.nan,
        axis=1,
    )
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

render_dashboard(data)

# Display additional tables or charts as necessary

# Run this from your command line:
# streamlit run your_script_name.py
