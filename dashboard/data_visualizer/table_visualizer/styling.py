# Third-party imports
import pandas as pd


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
                lambda row: color_format(row[col], row["your price total"]),
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
