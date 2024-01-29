"""
This module contains the TableVisualizer class, 
which is responsible for rendering data in the Streamlit application.

The TableVisualizer class provides methods to display data in 
a table format, perform statistical analysis, and apply styling to the tables.

Example usage:
    visualizer = TableVisualizer()
    visualizer.display(user_apartments_df, market_apartments_df)
"""
# Standard imports
from typing import Optional

# Third-party imports
import numpy as np
import pandas as pd
import streamlit as st

# Local imports
from dashboard.data_visualizer.data_preparation import (
    filter_data,
    compile_apartments_data,
    reorder_columns,
)

from dashboard.data_visualizer.table_visualizer.statistical_analysis import (
    compute_market_positioning_stats,
    aggregate_properties_data,
    calculate_price_by_model,
)

from dashboard.data_visualizer.table_visualizer.styling import (
    format_column_titles,
    add_styling_to_dataframe,
    display_header,
    display_html,
)

from dashboard.translations.translation_manager import Translation


class TableVisualizer:
    """
    A class responsible for rendering data in the Streamlit application.

    Attributes:
        display_settings: Configuration for the display settings of the visualizations.
        table_title (str): The title of the table.

    Methods:
        display: Display the data in a table format.
    """

    def __init__(
        self, display_settings: Optional[dict] = None, table_title: Optional[str] = None
    ):
        self.display_settings = display_settings
        self.selected_percentile: Optional[float] = None
        self.table_title: Optional[str] = table_title
        self.texts = Translation()["table"]

    def display(
        self, user_apartments_df: pd.DataFrame, market_apartments_df: pd.DataFrame
    ) -> None:
        """
        Display the data in a table format.

        Args:
            user_apartments_df (pd.DataFrame): A DataFrame containing your offers.
            market_apartments_df (pd.DataFrame): A DataFrame containing other offers.
        """

        user_apartments_narrowed, market_apartments_narrowed = filter_data(
            user_apartments_df, market_apartments_df
        )

        if self.table_title:
            display_header(
                *self.table_title,
            )

        self._select_price_percentile()

        apartments_comparison_df = compile_apartments_data(
            user_apartments_narrowed,
            market_apartments_narrowed,
            self.selected_percentile,
        )

        apartments_comparison_df["price_by_model"] = calculate_price_by_model(
            user_apartments_df
        )

        market_positioning_df = compute_market_positioning_stats(
            apartments_comparison_df
        )

        property_summary_df = aggregate_properties_data(apartments_comparison_df)

        apartments_comparison_df = reorder_columns(
            apartments_comparison_df,
            {
                "price_percentile": 7,
                "price_by_model": 8,
                "percentile_based_suggested_price": 9,
                "lease_time": 14,
            },
        )

        # Translate
        apartments_comparison_df = self._translate_dataframes_values(
            apartments_comparison_df
        )
        (
            apartments_comparison_df,
            market_positioning_df,
            property_summary_df,
        ) = self._translate_dataframes_column_names(
            [
                (
                    apartments_comparison_df,
                    self.texts["apartments"]["column_names"],
                ),
                (
                    market_positioning_df,
                    self.texts["market_positioning"]["column_names"],
                ),
                (
                    property_summary_df,
                    self.texts["summary_total_calculations"]["column_names"],
                ),
            ]
        )

        apartments_comparison_df = add_styling_to_dataframe(apartments_comparison_df)
        market_positioning_df = add_styling_to_dataframe(market_positioning_df)
        property_summary_df = add_styling_to_dataframe(property_summary_df)

        apartments_comparison_df = format_column_titles(apartments_comparison_df)
        market_positioning_df = format_column_titles(market_positioning_df)
        property_summary_df = format_column_titles(property_summary_df)

        display_header(subtitle=self.texts["market_positioning"]["main_title"])
        display_html(apartments_comparison_df, with_index=True)
        display_header(subtitle=self.texts["summary_total_calculations"]["main_title"])
        display_html(market_positioning_df)
        display_header(subtitle="\n\n")
        display_html(property_summary_df)

    def _translate_dataframes_values(self, apartments_comparison_df: pd.DataFrame):
        """
        Translate values in the DataFrame to the selected language.

        Args:
            apartments_comparison_df (pd.DataFrame): A DataFrame containing offers data.

        Returns:
            pd.DataFrame: A DataFrame with translated values.
        """

        # Translate boolean values
        boolean_column = "is_furnished"
        if boolean_column in apartments_comparison_df.columns:
            apartments_comparison_df[boolean_column] = self._translate_boolean_values(
                apartments_comparison_df[boolean_column]
            )

        # Translate time periods values
        period_format_column = "lease_time"
        if period_format_column in apartments_comparison_df.columns:
            apartments_comparison_df[
                period_format_column
            ] = self._translate_periods_values(
                apartments_comparison_df[period_format_column]
            )

        return apartments_comparison_df

    def _select_price_percentile(self) -> None:
        """
        Display a selection box for choosing a price percentile.
        """

        column_1, column_2, column_3 = st.columns([1, 1, 1])

        title = self.texts["apartments"]["percentile_dropdown"]

        with column_2:
            self.selected_percentile = st.selectbox(
                title,
                options=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                index=4,  # Default to 0.5
            )

    def _translate_boolean_values(
        self,
        series: pd.Series,
    ):
        """
        Translate boolean values to the selected language.

        Args:
            series (pd.Series): A Series containing boolean values.
        """
        boolean_values: dict[str, str] = self.texts["apartments"]["column_values"][
            "boolean"
        ]
        yes = boolean_values["True"]
        no = boolean_values["False"]

        def translate(boolean: str):
            """Translate boolean in the HTML strings"""

            if boolean is True:
                return yes
            elif boolean is False:
                return no
            else:
                raise ValueError(
                    "The series must contain only boolean values:\n"
                    f"value to be replaced:|{boolean}|\n"
                    f"replacing value:     |{yes}|{no}|\n"
                )

        series = series.apply(translate)
        return series

    def _translate_periods_values(
        self,
        series: pd.Series,
    ):  # TODO move it one level higher to table_visualizer.py
        """
        Translate time periods values to the selected language.

        Args:
            series (pd.Series): A Series containing time periods values.
        """
        time_intervals: dict[str, str] = self.texts["apartments"]["column_values"][
            "time_intervals"
        ]

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

    def _translate_dataframes_column_names(
        self, list_of_dataframes_and_keys: list[tuple[pd.DataFrame, Translation]]
    ):
        """
        Translate dataframes columns names to the selected language.

        Args:
            list_of_dataframes_and_keys (list[tuple[pd.DataFrame, Translation]]):
            A list of tuples containing a DataFrame and a Translation object.

        Returns:
            list[pd.DataFrame]: A list of DataFrames with translated columns names.
        """
        dfs = []
        for df, key in list_of_dataframes_and_keys:
            df = self._rename_with_check(df, key)
            dfs.append(df)

        return dfs

    def _rename_with_check(
        self, df: pd.DataFrame, translation_dict: [str, str]
    ) -> pd.DataFrame:
        """
        Checks column coverage and renames DataFrame columns.

        Args:
            df (pd.DataFrame): DataFrame to be processed.
            translation_key (str): Key for accessing the translation dictionary.

        Returns:
            pd.DataFrame: DataFrame with renamed columns.
        """
        self._check_column_coverage(df, translation_dict)
        return df.rename(columns=translation_dict)

    def _check_column_coverage(self, df: pd.DataFrame, translation_dict: dict):
        df_columns = set(df.columns)
        translation_keys = set(translation_dict.keys())

        missing_in_df = translation_keys - df_columns
        missing_in_translation = df_columns - translation_keys

        if missing_in_df or missing_in_translation:
            error_message = ""
            if missing_in_df:
                error_message += f"Columns missing in DataFrame: {missing_in_df}\n"
            if missing_in_translation:
                error_message += (
                    f"Columns missing in Translation: {missing_in_translation}\n"
                )
            raise ValueError(error_message)
