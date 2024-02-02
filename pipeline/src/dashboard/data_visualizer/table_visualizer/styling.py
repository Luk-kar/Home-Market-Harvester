"""
This module provides functions for applying custom styling 
to DataFrames and displaying them as formatted tables.
"""

# Standard imports
import re

# Third-party imports
import pandas as pd
import streamlit as st

# Local imports
from dashboard.translations.translation_manager import Translation


def apply_custom_styling(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply custom styling to a DataFrame's elements.

    Args:
        df (pd.DataFrame): A DataFrame containing offers data.

    Returns:
        pd.DataFrame: A DataFrame with custom styling applied.
    """
    column_values = Translation()["table"]["apartments"]["column_values"]
    boolean_values = column_values["boolean"]
    true = boolean_values["True"]
    false = boolean_values["False"]
    nan = column_values["time_intervals"]["nan"]

    def apply_row_styles(row):
        for col in row.index:
            if isinstance(row[col], str) and re.match(r"\+\d", row[col]):
                row[col] = f'<span style="color: green;">{row[col]}</span>'
            elif isinstance(row[col], str) and re.match(r"-\d", row[col]):
                row[col] = f'<span style="color: red;">{row[col]}</span>'
            elif row[col] == true:
                row[col] = f'<span style="color: green;">{true}</span>'
            elif row[col] == false:
                row[col] = f'<span style="color: red;">{false}</span>'
            elif row[col] == nan:
                row[col] = f'<span style="color: grey;">{nan}</span>'
        return row

    return df.apply(apply_row_styles, axis=1)


def display_html(styled_df: pd.DataFrame, with_index: bool = False) -> None:
    """
    Display a DataFrame as a formatted table.

    Args:
        styled_df (pd.DataFrame): A DataFrame with custom styling applied.
        with_index (bool): Whether to display the DataFrame index.
    """
    html = styled_df.to_html(escape=False, index=with_index)
    centered_html = f"""
        <div style='display: flex; justify-content: center; align-items: center; height: 100%;'>
            <div style='text-align: center;'>{html}</div>
        </div>
        """
    st.markdown(centered_html, unsafe_allow_html=True)


def format_column_titles(apartments_df: pd.DataFrame) -> pd.DataFrame:
    """
    Format the column titles to be more readable.

    Args:
        apartments_df (pd.DataFrame): A DataFrame containing offers data.

    Returns:
        pd.DataFrame: A DataFrame with formatted column titles.
    """

    apartments_df.columns = [col.replace("_", " ") for col in apartments_df.columns]

    return apartments_df


def display_header(text: str = "", subtitle: str = "") -> None:
    """
    Display a formatted header.

    Args:
        text (str, optional): The header text. Defaults to "".
        subtitle (str, optional): The header subtitle. Defaults to "".
    """
    st.markdown(
        f"<h3 style='text-align: center;'>{text}</h3>",
        unsafe_allow_html=True,
    )

    if subtitle:
        st.markdown(
            f"<p style='text-align: center;'>{subtitle}</p>",
            unsafe_allow_html=True,
        )


def add_styling_to_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add custom styling to a DataFrame.

    Args:
        df (pd.DataFrame): A DataFrame containing offers data.

    Returns:
        pd.DataFrame: A DataFrame with custom styling applied.
    """

    table_columns = Translation()["table"]

    plus_minus_columns = [
        table_columns["apartments"]["column_names"]["price_by_model"],
        table_columns["apartments"]["column_names"]["percentile_based_suggested_price"],
        table_columns["apartments"]["column_names"]["price_per_meter_by_percentile"],
        table_columns["apartments"]["column_names"]["percentile_based_suggested_price"],
        table_columns["market_positioning"]["column_names"]["avg_price_by_model"],
        table_columns["market_positioning"]["column_names"][
            "avg_price_per_meter_by_percentile"
        ],
        table_columns["market_positioning"]["column_names"][
            "avg_percentile_based_suggested_price"
        ],
    ]
    round_float_columns(df, plus_minus_columns)
    apply_plus_minus_formatting(df, plus_minus_columns)

    percent_columns = [
        table_columns["apartments"]["column_names"]["price_per_meter_by_percentile"],
        table_columns["market_positioning"]["column_names"][
            "avg_price_per_meter_by_percentile"
        ],
    ]
    append_percent_sign(df, percent_columns)

    color_difference_columns = [
        table_columns["summary_total_calculations"]["column_names"][
            "price_total_per_model"
        ],
        table_columns["summary_total_calculations"]["column_names"][
            "percentile_based_suggested_price_total"
        ],
    ]

    apply_color_based_on_difference(df, color_difference_columns)

    styled_df = apply_custom_styling(df)

    return styled_df


def apply_plus_minus_formatting(df: pd.DataFrame, columns: list[str]) -> None:
    """
    Apply plus-minus formatting to the specified columns.

    Args:
        df (pd.DataFrame): A DataFrame containing offers data.
        columns (list[str]): A list of column names to format.
    """
    for col in columns:
        if col in df.columns:
            df[col] = df[col].apply(format_with_plus_sign)


def round_float_columns(df: pd.DataFrame, columns: list[str]) -> None:
    """
    Round float columns to two decimal places.

    Args:
        df (pd.DataFrame): A DataFrame containing offers data.
        columns (list[str]): A list of column names to format.
    """
    float_columns = df.select_dtypes(include=["float"]).columns
    for col in float_columns:
        if col not in columns:
            df[col] = df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else x)


def append_percent_sign(df: pd.DataFrame, columns: list[str]) -> None:
    """
    Append a percent sign to the specified columns.

    Args:
        df (pd.DataFrame): A DataFrame containing offers data.
        columns (list[str]): A list of column names to format.
    """
    for col in columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: f"{x}%" if pd.notna(x) else x)


def apply_color_based_on_difference(df: pd.DataFrame, columns: list[str]) -> None:
    """
    Apply color formatting to the specified columns based on the difference between
    the column value and the 'your price total' column.

    Args:
        df (pd.DataFrame): A DataFrame containing offers data.
        columns (list[str]): A list of column names to format.
    """
    for col in columns:
        if col in df.columns:
            df[col] = df.apply(
                lambda row, c=col: color_format(
                    row[c],
                    row[
                        Translation()["table"]["summary_total_calculations"][
                            "column_names"
                        ]["your_price_total"]
                    ],
                ),
                axis=1,
            )


def format_with_plus_sign(value) -> str:
    """
    Format a value with a plus sign if it is positive.

    Args:
        value: The value to format.

    Returns:
        str: The formatted value."""

    if pd.isna(value):
        return value
    elif isinstance(value, (float, int)) and value > 0:
        return f"+{value:.2f}"
    elif isinstance(value, (float, int)):
        return f"{value:.2f}"
    else:
        return value


def color_format(value, comparison_value):
    """
    Apply color formatting to a value based on the difference between the value and
    the comparison value.

    Args:
        value: The value to format.
        comparison_value: The value to compare to.

    Returns:
        str: The formatted value.
    """
    if pd.isna(value) or pd.isna(comparison_value):
        return value
    if value < comparison_value:
        color = "red"
    elif value > comparison_value:
        color = "green"
    else:
        color = "grey"
    return f"<span style='color: {color};'>{value}</span>"
