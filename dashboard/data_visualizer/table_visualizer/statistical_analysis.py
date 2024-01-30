"""
This module contains functions for statistical analysis of the data.
"""

# Third-party imports
import pandas as pd

# Local imports
from dashboard.config import MODEL
from dashboard.data_visualizer.table_visualizer.styling import (
    format_with_plus_sign,
)
from dashboard.data_visualizer.table_visualizer.model_offer_predictor import (
    ModelPredictor,
)


def compute_market_positioning_stats(
    apartments_comparison_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate and return market positioning data.

    Args:
        apartments_comparison_df (pd.DataFrame): A DataFrame containing offers data.

    Returns:
        pd.DataFrame: A DataFrame containing market positioning data.
    """

    summary_stats = {
        "flats": len(apartments_comparison_df["flat_id"].unique()),
        "floor_max": apartments_comparison_df["floor"].max(),
        "avg_area": apartments_comparison_df["area"].mean(),
        "furnished_sum": apartments_comparison_df["is_furnished"].sum(),
        "avg_your_price": apartments_comparison_df["your_price"].mean(),
        "avg_price_percentile": apartments_comparison_df["price_percentile"].mean(),
        "avg_price_by_model": apartments_comparison_df["price_by_model"].mean(),
        "avg_percentile_based_suggested_price": apartments_comparison_df[
            "percentile_based_suggested_price"
        ].mean(),
        "avg_your_price_per_meter": apartments_comparison_df[
            "your_price_per_meter"
        ].mean(),
        "avg_price_per_meter_by_percentile": apartments_comparison_df[
            "price_per_meter_by_percentile"
        ].mean(),
    }
    market_positioning_summary_df = pd.DataFrame([summary_stats])

    plus_minus_columns = [
        "avg_price_by_model",
        "avg_suggested_price_by_median",
        "price_per_meter_by_percentile",
    ]

    # Custom formatting function to add '+' for positive values
    # Apply the formatting function to the specific columns
    for col in plus_minus_columns:
        if col in market_positioning_summary_df.columns:
            market_positioning_summary_df[col] = market_positioning_summary_df[
                col
            ].apply(format_with_plus_sign)

    return market_positioning_summary_df


def aggregate_properties_data(apartments_comparison_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate and return summary data for properties.

    Args:
        apartments_comparison_df (pd.DataFrame): A DataFrame containing offers data.

    Returns:
        pd.DataFrame: A DataFrame containing summary data for properties.
    """
    actual_price_total = apartments_comparison_df["your_price"].sum()

    price_total_per_model = (
        actual_price_total + apartments_comparison_df["price_by_model"].sum()
    )  # price by model is additional sum

    percentile_based_suggested_price_total = (
        actual_price_total
        + apartments_comparison_df["percentile_based_suggested_price"].sum()
    )  # price by median is additional sum

    summary_data = pd.DataFrame(
        {
            "your_price_total": [actual_price_total],
            "price_total_per_model": [price_total_per_model],
            "percentile_based_suggested_price_total": [
                percentile_based_suggested_price_total
            ],
        }
    )

    return summary_data


def calculate_percentile_based_suggested_price(
    apartments_df: pd.DataFrame, market_apartments_df: pd.DataFrame, percentile: int
) -> pd.Series:
    """
    Calculate the suggested price based on percentile for each apartment.

    Args:
        apartments_df (pd.DataFrame): A DataFrame containing offers data.
        market_apartments_df (pd.DataFrame): A DataFrame containing other offers.
        percentile (int): The percentile to use for the calculation.

    Returns:
        pd.Series: A Series containing the suggested prices
    """

    def calculate_price(row):
        furnished_offers = market_apartments_df[
            market_apartments_df["equipment"]["furniture"] == True
        ]
        non_furnished_offers = market_apartments_df[
            market_apartments_df["equipment"]["furniture"] == False
        ]

        sq_meter_price = None
        if row["is_furnished"]:
            sq_meter_price = furnished_offers["pricing"]["total_rent_sqm"].quantile(
                percentile
            )
        else:
            sq_meter_price = non_furnished_offers["pricing"]["total_rent_sqm"].quantile(
                percentile
            )

        total_price_difference = sq_meter_price * row["area"] - row["your_price"]
        return total_price_difference

    return apartments_df.apply(calculate_price, axis=1)


def calculate_yours_price_percentile_against_others(
    apartments_df: pd.DataFrame, market_apartments_df: pd.DataFrame
) -> pd.Series:
    """
    Calculate the percentile of user the price compared to the market offers.
    """

    def calculate_percentile(row, prices_series):
        return prices_series[prices_series <= row["your_price"]].count() / len(
            prices_series
        )

    furnished_prices = market_apartments_df[
        market_apartments_df["equipment"]["furniture"] == True
    ]["pricing"]["total_rent"]
    non_furnished_prices = market_apartments_df[
        market_apartments_df["equipment"]["furniture"] == False
    ]["pricing"]["total_rent"]

    furnished_prices_series = pd.Series(furnished_prices.values)
    non_furnished_prices_series = pd.Series(non_furnished_prices.values)

    return apartments_df.apply(
        lambda row: calculate_percentile(
            row,
            furnished_prices_series
            if row["is_furnished"]
            else non_furnished_prices_series,
        ),
        axis=1,
    )


def calculate_price_per_meter_differences(
    apartments_df: pd.DataFrame,
    market_apartments_df: pd.DataFrame,
    selected_percentile: float,
) -> pd.Series:
    """
    Calculate the price per meter differences for each apartment.
    """

    def calculate_difference(row):
        furnished_offers = market_apartments_df[
            market_apartments_df["equipment"]["furniture"] == True
        ]
        non_furnished_offers = market_apartments_df[
            market_apartments_df["equipment"]["furniture"] == False
        ]

        sq_meter_price_others = (
            furnished_offers["pricing"]["total_rent_sqm"].quantile(selected_percentile)
            if row["is_furnished"]
            else non_furnished_offers["pricing"]["total_rent_sqm"].quantile(
                selected_percentile
            )
        )

        sq_meter_price_yours = row["your_price_per_meter"]
        percent_difference = round(
            ((sq_meter_price_others / sq_meter_price_yours) - 1) * 100, 2
        )
        return percent_difference

    return apartments_df.apply(calculate_difference, axis=1)


def calculate_price_by_model(
    apartments_df: pd.DataFrame,
) -> pd.Series:
    """
    Calculate price by model.
    """
    model_path = MODEL["model_path"]

    predictor = ModelPredictor(model_path)
    price_predictions = predictor.get_price_predictions(apartments_df)
    price_by_model_df = pd.Series(price_predictions)
    price_by_model_df = price_by_model_df.apply(round_to_nearest_fifty)

    price_by_model_diff = price_by_model_df - apartments_df["price"]

    return price_by_model_diff


def round_to_nearest_fifty(number: float) -> int:
    """
    Round a number to the nearest 50.
    """
    round_to = 50
    return round(number / round_to) * round_to
