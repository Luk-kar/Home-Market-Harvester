"""
This module provides functions for applying custom styling 
to DataFrames and displaying them as formatted tables.
"""

# Third-party imports
import numpy as np
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

    def apply_row_styles(row):
        for col in row.index:
            if isinstance(row[col], str) and row[col].startswith("+"):
                row[col] = f'<span style="color: green;">{row[col]}</span>'
            elif isinstance(row[col], str) and row[col].startswith("-"):
                row[col] = f'<span style="color: red;">{row[col]}</span>'
            elif row[col] is True:
                row[col] = '<span style="color: green;">True</span>'
            elif row[col] is False:
                row[col] = '<span style="color: red;">False</span>'
        return row

    return df.apply(apply_row_styles, axis=1)


def display_html(styled_df: pd.DataFrame, with_index: bool) -> None:
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


def show_data_table(df: pd.DataFrame, with_index: bool = False) -> None:
    """
    Display a formatted table of the DataFrame.

    Args:
        df (pd.DataFrame): A DataFrame containing offers data.
        with_index (bool, optional): Whether to display the DataFrame index. Defaults to False.
    """

    plus_minus_columns = [
        "price by model",
        "suggested price by percentile",
        "price per meter by percentile",
        "avg price by model",
        "avg suggested price by percentile",
        "avg price per meter by percentile",
        "percentile based suggested price",
        "avg percentile based suggested price",
    ]
    round_float_columns(df, plus_minus_columns)
    apply_plus_minus_formatting(df, plus_minus_columns)

    percent_columns = [
        "price per meter by percentile",
        "avg price per meter by percentile",
    ]
    append_percent_sign(df, percent_columns)

    color_difference_columns = [
        "price total per model",
        "percentile based suggested price total",
    ]
    apply_color_based_on_difference(df, color_difference_columns)

    print(df.columns)

    styled_df = apply_custom_styling(df)

    # TODO move it one level higher to table_visualizer.py
    # Translate
    boolean_column = "is_furnished".replace("_", " ")
    if boolean_column in styled_df.columns:
        styled_df[boolean_column] = _translate_boolean_values(styled_df[boolean_column])
    period_format_column = "lease_time".replace("_", " ")
    if period_format_column in styled_df.columns:
        styled_df[period_format_column] = _translate_periods_values(
            styled_df[period_format_column]
        )

    # styled_df = _translate_columns(styled_df)

    display_html(styled_df, with_index)


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
                lambda row, c=col: color_format(row[c], row["your price total"]),
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


def _translate_boolean_values(
    series: pd.Series,
):  # TODO move it one level higher to table_visualizer.py
    """
    Translate boolean values to the selected language.

    Args:
        series (pd.Series): A Series containing boolean values.
    """
    boolean_values: dict[str, str] = Translation()["table"]["apartments"][
        "column_values"
    ]["boolean"]
    yes = boolean_values["True"]
    no = boolean_values["False"]
    true = str(True)
    false = str(False)

    def translate(boolean: str):
        """Translate boolean in the HTML strings"""
        if true in boolean:
            return boolean.replace(true, yes)
        elif false in boolean:
            return boolean.replace(false, no)
        else:
            raise ValueError(
                "The series must contain only boolean values:\n"
                f"value to be replaced:|{boolean}|\n"
                f"replacing value:     |{yes}|{no}|\n"
            )

    series = series.apply(translate)
    return series


def _translate_periods_values(
    series: pd.Series,
):  # TODO move it one level higher to table_visualizer.py
    """
    Translate time periods values to the selected language.

    Args:
        series (pd.Series): A Series containing time periods values.
    """
    time_intervals: dict[str, str] = Translation()["table"]["apartments"][
        "column_values"
    ]["time_intervals"]

    def translate(time_period: str | np.float64):
        """
        The periods in db are like:
        'NaN', '1 day', '2 days', '1 week', '2 weeks', '1 month', '2 months', '1 year', '2 years'
        """
        if pd.isna(time_period):
            return time_intervals["nan"]
        else:
            for key in time_intervals.keys():
                if key in time_period:
                    return time_period.replace(key, time_intervals[key])
            raise ValueError(
                "The series contains an unrecognized time period value:\n"
                f"value to be replaced: |{time_period}|\n"
                f"replacing value:      |{time_intervals}|\n"
            )

    series = series.apply(translate)
    return series


def _translate_columns(styled_df: pd.DataFrame) -> pd.DataFrame:
    """
    Translate the column names to the selected language.

    Args:
        styled_df (pd.DataFrame): A DataFrame with custom styling applied.

    Returns:
        pd.DataFrame: A DataFrame with translated column names.
    """
    column_translation = Translation()["table"]["apartments"]["column_names"]
    modified_translation = {}

    for original_key, translated_key in column_translation.items():
        modified_key = original_key.replace("_", " ")
        modified_translation[modified_key] = translated_key

    # Check if there are any keys left in modified_translation
    # that are not mapped to columns
    modified_translation = {
        key: val
        for key, val in modified_translation.items()
        if key in styled_df.columns
    }
    unmapped_keys = set(modified_translation.keys()) - set(styled_df.columns)
    if unmapped_keys:
        raise ValueError(f"Unmapped translation keys: {unmapped_keys}")
    styled_df = styled_df.rename(columns=modified_translation)

    return styled_df
