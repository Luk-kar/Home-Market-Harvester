# Standard imports
from typing import Tuple, Optional

# Third-party imports
import pandas as pd
import streamlit as st

# Local imports
from dashboard.data_visualizer.table_visualizer.data_preparation import (
    filter_data,
    compile_apartments_data,
    # compute_market_positioning_stats,
    # aggregate_properties_data,
    reorder_columns,
)

from dashboard.data_visualizer.table_visualizer.statistical_analysis import (
    compute_market_positioning_stats,
    aggregate_properties_data,
    calculate_price_by_model,
)

from dashboard.data_visualizer.table_visualizer.styling import (
    apply_plus_minus_formatting,
    round_float_columns,
    append_percent_sign,
    apply_color_based_on_difference,
    format_column_titles,
    show_data_table,
    display_header,
)


# TODO is furnished adjust to the offers
class TableVisualizer:
    def __init__(
        self, display_settings: Optional[dict] = None, table_title: Optional[str] = None
    ):
        self.display_settings = display_settings
        self.selected_percentile: Optional[float] = None
        self.table_title: Optional[str] = table_title

    def display(
        self, user_apartments_df: pd.DataFrame, market_apartments_df: pd.DataFrame
    ) -> None:
        """
        Display the data in a table format.
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

        apartments_comparison_df = format_column_titles(apartments_comparison_df)
        market_positioning_df = format_column_titles(market_positioning_df)
        property_summary_df = format_column_titles(property_summary_df)

        show_data_table(apartments_comparison_df, with_index=True)
        display_header(subtitle="📈 Market Positioning")
        show_data_table(market_positioning_df)
        display_header(subtitle="📋 Total Summary")
        show_data_table(property_summary_df)
        display_header(subtitle="\n\n")

    def _select_price_percentile(self) -> None:
        """
        Display a selection box for choosing a price percentile.
        """

        column_1, column_2, column_3 = st.columns([1, 1, 1])

        with column_2:
            self.selected_percentile = st.selectbox(
                "Select Percentile for Suggested Price Calculation",
                options=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                index=4,  # Default to 0.5
            )

    # def _round_to_nearest_hundred(
    #     self, number: float
    # ) -> int:  # TODO statistical analysis
    #     return round(number / 100) * 100

    # def _format_with_plus_sign(self, value) -> str:
    #     """
    #     Format a value with a '+' sign if it is positive.
    #     """
    #     if pd.isna(value):
    #         return value
    #     elif isinstance(value, (float, int)) and value > 0:
    #         return f"+{value:.2f}"
    #     elif isinstance(value, (float, int)):
    #         return f"{value:.2f}"
    #     else:
    #         return value

    # def _display_html(
    #     self, styled_df: pd.DataFrame, with_index: bool
    # ) -> None:  # TODO styling
    #     html = styled_df.to_html(escape=False, index=with_index)
    #     centered_html = f"""
    #     <div style='display: flex; justify-content: center; align-items: center; height: 100%;'>
    #         <div style='text-align: center;'>{html}</div>
    #     </div>
    #     """
    #     st.markdown(centered_html, unsafe_allow_html=True)
