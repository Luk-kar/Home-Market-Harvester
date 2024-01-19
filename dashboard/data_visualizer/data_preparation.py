"""
This module contains functions for data preparation and manipulation 
in the context of apartment rental analysis.
"""

# Standard imports
from typing import Tuple

# Third-party imports
import pandas as pd

# Local imports
from data_visualizer.table_visualizer.statistical_analysis import (
    calculate_percentile_based_suggested_price,
    calculate_yours_price_percentile_against_others,
    calculate_price_per_meter_differences,
)


def filter_data(
    user_apartments_df: pd.DataFrame, market_apartments_df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Filter the data to only include apartments that are relevant for the analysis.

    Args:
        user_apartments_df (pd.DataFrame): A DataFrame containing your offers.
        market_apartments_df (pd.DataFrame): A DataFrame containing other offers.

    Returns:
        tuple: A tuple containing DataFrames for your offers and other offers.
    """

    selected_columns = [
        "deal_id",
        "flat_id",
        "floor",
        "number_of_rooms",
        "area",
        "is_furnished",
        "price",
        # "deposit",
        "lease_time",
        "price_per_meter",
    ]
    user_apartments_df = user_apartments_df[selected_columns]

    filtered_df = market_apartments_df[
        market_apartments_df.apply(matches_city_building_year_criteria, axis=1)
    ].copy()

    user_apartments_df = user_apartments_df.rename(
        columns={"price_per_meter": "your_price_per_meter"}
    )

    return user_apartments_df, filtered_df


def matches_city_building_year_criteria(row: pd.Series) -> bool:
    """
    Filter rows based on the following criteria:
    - City is in the list of cities
    - Building type is in the list of building types
    - Build year is less than or equal to 1970

    Args:
        row (pd.Series): A row of a DataFrame.

    Returns:
        bool: True if the row meets the criteria, False otherwise.
    """
    try:
        city = row["location"]["city"]
        building_type = (
            row["type_and_year"]["building_type"]
            if pd.notna(row["type_and_year"].get("building_type"))
            else False
        )
        build_year = (
            row["type_and_year"]["build_year"]
            if pd.notna(row["type_and_year"].get("build_year"))
            else False
        )
        return (
            city
            in [
                "będziński",
                "Zawada",
                "Siewierz",
                "tarnogórski",
                "Piekary Śląskie",
                "zawierciański",
                "Siemianowice Śląskie",
            ]
            and building_type in ["block_of_flats", "apartment_building"]
            and build_year <= 1970
        )
    except KeyError:
        return False


def reorder_columns(df: pd.DataFrame, column_order: dict) -> pd.DataFrame:
    """
    Reorder the columns of a DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to reorder.
        column_order (dict): A dictionary mapping column names to their new positions.

    Returns:
        pd.DataFrame: The DataFrame with reordered columns.
    """
    columns = list(df.columns)
    for column_name, new_position in column_order.items():
        if column_name in columns:
            columns.insert(new_position, columns.pop(columns.index(column_name)))
        else:
            print(f"Column '{column_name}' not found in DataFrame.")
    return df[columns]


def compile_apartments_data(
    user_apartments_df: pd.DataFrame,
    market_apartments_df: pd.DataFrame,
    percentile: float,
) -> pd.DataFrame:
    """
    Compile data from user apartments and market apartments into a single DataFrame.

    Args:
        user_apartments_df (pd.DataFrame): A DataFrame containing your offers.
        market_apartments_df (pd.DataFrame): A DataFrame containing other offers.

    Returns:
        pd.DataFrame: A DataFrame containing the compiled data.
    """

    apartments_df = user_apartments_df.copy()

    apartments_df = apartments_df.rename(
        columns={"price": "your_price", "deal_id": "rental_start"}
    )

    apartments_df[
        "percentile_based_suggested_price"
    ] = calculate_percentile_based_suggested_price(
        apartments_df, market_apartments_df, percentile
    )

    apartments_df["price_percentile"] = calculate_yours_price_percentile_against_others(
        apartments_df, market_apartments_df
    )

    apartments_df[
        "price_per_meter_by_percentile"
    ] = calculate_price_per_meter_differences(
        apartments_df, market_apartments_df, percentile
    )

    return apartments_df
