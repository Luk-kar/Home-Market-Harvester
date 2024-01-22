"""
This module contains the BarChartVisualizer class, 
which is responsible for creating and displaying bar chart visualizations.
"""

# Standard imports
from typing import Any, Dict, List, Optional

# Third-party imports
import matplotlib.axes._axes as Axes
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

# Local imports
from dashboard.data_visualizer.data_preparation import (
    matches_city_building_year_criteria,
)
from dashboard.translations.translation_manager import Translation


class BarChartVisualizer:
    """
    BarChartVisualizer is responsible for creating and displaying bar chart visualizations.

    Attributes:
        display_settings (Dict[str, Any]): A dictionary containing display settings.
        user_apartments_df (pd.DataFrame): A DataFrame containing user apartment offers data.
        market_apartments_df (pd.DataFrame): A DataFrame containing market apartment offers data.
        similar_apartments_df (pd.DataFrame): A DataFrame containing similar apartment offers data.
        bar_chart_title (str): A title for the bar chart.
    """

    def __init__(
        self,
        display_settings: Dict[str, Any],
        user_apartments_df: pd.DataFrame,
        market_apartments_df: pd.DataFrame,
        bar_chart_title: str,
    ):
        self.display_settings = display_settings
        self.user_apartments_df = user_apartments_df
        self.market_apartments_df = market_apartments_df
        self.similar_apartments_df = self._filter_similar_to_user_offers(
            market_apartments_df
        )
        self.bar_chart_title = bar_chart_title

        """
        Initializes the bar chart visualizer with necessary data.
        """

    def display(self) -> None:
        """
        Displays the bar chart.
        """
        if self.bar_chart_title:
            st.markdown(
                f"<h3 style='text-align: center;'>{self.bar_chart_title}</h3>",
                unsafe_allow_html=True,
            )

        offers = self._create_offers_dict()

        price_per_meter_col, price_per_offer_col = st.columns(2)

        categories = Translation()["char_chart"]["y_axis_offers"].values()

        xlabel = self._generate_x_label(categories)
        ylabel = Translation()["char_chart"]["x_axis_price"]

        with price_per_meter_col:
            per_meter_data = self._calculate_median_data(offers, "price_per_meter")
            st.pyplot(
                self._plot_bar_chart(
                    per_meter_data,
                    Translation()["char_chart"]["charts_titles"]["price_per_meter"],
                    xlabel,
                    ylabel,
                )
            )

        with price_per_offer_col:
            per_offer_data = self._calculate_median_data(offers, "price")
            st.pyplot(
                self._plot_bar_chart(
                    per_offer_data,
                    Translation()["char_chart"]["charts_titles"]["price_per_offer"],
                    xlabel,
                    ylabel,
                )
            )

    def _filter_similar_to_user_offers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter DataFrame rows based on the following criteria:
        - City is in the list of cities
        - Building type is in the list of building types
        - Build year is less than or equal to 1970

        Args:
            df (pd.DataFrame): A DataFrame containing offers data.

        Returns:
            pd.DataFrame: A DataFrame containing offers data filtered by the criteria.
        """

        return df[df.apply(matches_city_building_year_criteria, axis=1)]

    def _generate_x_label(self, categories: List[str]) -> str:
        """
        Generates a label for the x-axis of the bar chart.

        Args:
            categories (List[str]): A list of categories.

        Returns:
            str: A label for the x-axis of the bar chart.
        """
        space = " " * 36
        max_length = max(len(category) for category in categories)
        centered_categories = [category.center(max_length) for category in categories]
        return space.join(centered_categories)

    def _calculate_median_data(
        self, offers: Dict[str, Dict[str, pd.DataFrame]], column: str
    ) -> Dict[str, float]:
        """
        Calculates the median price per meter for each offer category.

        Args:
            offers (Dict[str, Dict[str, pd.DataFrame]]): A dictionary of offers for each category.
            column (str): The column to calculate the median for.

        Returns:
            Dict[str, float]: A dictionary containing the median price per meter
            for each offer category.
        """

        ADDITIONAL_SPACING = {
            "Yours": -1,
            "Similar": None,
            "All in 20 km radius": 0,
        }

        COLUMN_MAPPINGS = {
            "price": ("price", ("pricing", "total_rent")),
            "price_per_meter": ("price_per_meter", ("pricing", "total_rent_sqm")),
        }

        def _calculate_furniture_and_categories_medians(
            furnishings: Dict[str, pd.DataFrame], category: str, column: str
        ) -> Dict[str, float]:
            """
            Processes the furnishings for a given category.
            """
            result = {}
            primary_col, fallback_col = COLUMN_MAPPINGS.get(column, (None, None))
            for furniture, df in furnishings.items():
                price_column = (
                    primary_col if primary_col in df.columns else fallback_col
                )
                if not price_column:
                    continue  # Handle the case where price_column is not found

                median = df[price_column].median().round(2)
                position_to_add_space = ADDITIONAL_SPACING.get(category)
                column_name = self._format_column_name_for_display(
                    furniture, position_to_add_space
                )
                result[column_name] = median
            return result

        data = {}
        for category, furnishings in offers.items():
            data.update(
                _calculate_furniture_and_categories_medians(
                    furnishings, category, column
                )
            )
        return data

    def _format_column_name_for_display(
        self, furniture: str, position_to_add_space: Optional[int]
    ) -> str:
        """
        This method provides a clever workaround to create visually similar names
        for bar chart columns by strategically inserting spaces
        at various positions along the edges of the names.
        While the resulting strings are technically different,
        they appear identical when displayed.
        This approach ensures that column names remain distinct
        and are not inadvertently overwritten.

        Args:
            furniture (str): The furniture type.
            position_to_add_space (Optional[int]): The position to add a space at.

        Returns:
            str: The formatted column name.
        """

        if position_to_add_space is None:
            return furniture
        else:
            return self._insert_char(furniture, position_to_add_space, " ")

    def _insert_char(
        self, original_string: str, position: int, char_to_insert: str
    ) -> str:
        """
        Inserts a character at the specified position in a string.

        Args:
            original_string (str): The original string.
            position (int): The position to insert the character at.
            char_to_insert (str): The character to insert.

        Returns:
            str: The updated string.
        """

        is_position_beyond_string = position >= len(original_string)
        is_negative_position_invalid = position < 0 and abs(position) >= len(
            original_string
        )

        position_out_of_range = (
            is_position_beyond_string or is_negative_position_invalid
        )

        if position_out_of_range:
            raise IndexError(
                f"Position is out of range.\nPosition: {position},\nRange: {len(original_string)}"
            )

        # Adjust the position for negative indices
        if position < 0:
            position = len(original_string) + position + 1

        changed_string = (
            original_string[:position] + char_to_insert + original_string[position:]
        )

        return changed_string

    def _create_offers_dict(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Creates a dictionary of offers for each category.

        Returns:
            Dict[str, Dict[str, pd.DataFrame]]: A dictionary of offers for each category.
        """
        user_df = self.user_apartments_df
        similar_df = self.similar_apartments_df
        whole_market_df = self.market_apartments_df

        return {
            "Yours": {
                "furnished": user_df[user_df["is_furnished"] == True],
                "unfurnished": user_df[user_df["is_furnished"] == False],
            },
            "Similar": {
                "furnished": similar_df[
                    (similar_df["equipment"]["furniture"] == True)
                    & (similar_df["location"]["city"] == "będziński")
                ],
                "unfurnished": similar_df[
                    (similar_df["equipment"]["furniture"] == False)
                    & (similar_df["location"]["city"] == "będziński")
                ],
            },
            "All in 20 km radius": {
                "furnished": whole_market_df[
                    whole_market_df["equipment"]["furniture"] == True
                ],
                "unfurnished": whole_market_df[
                    whole_market_df["equipment"]["furniture"] == False
                ],
            },
        }

    def _get_darker_shade(self, color: str, factor: float = 0.5) -> str:
        """
        Darkens a color by a specified factor.

        Args:
            color (str): The color to darken.
            factor (float): The factor to darken the color by.

        Returns:
            str: The darkened color.
        """
        rgb = mcolors.hex2color(color)
        darkened_rgb = [max(0, c * factor) for c in rgb]
        darkened_hex = mcolors.rgb2hex(darkened_rgb)
        return darkened_hex

    def _set_plot_aesthetics(
        self,
        axes: Axes,
        title: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
    ) -> None:
        """
        Sets the aesthetics of the plot.

        Args:
            axes: The axes to set the aesthetics for.
            title (Optional[str], optional): The title of the plot. Defaults to None.
            xlabel (Optional[str], optional): The label for the x-axis. Defaults to None.
            ylabel (Optional[str], optional): The label for the y-axis. Defaults to None.
        """

        display_settings = self.display_settings

        # Set the title and axis labels
        if title:
            axes.set_title(
                title,
                color=display_settings["label_color"],
                fontweight=display_settings["fontweight"],
            )
        if xlabel:
            axes.set_xlabel(xlabel, fontweight=display_settings["fontweight"])
        if ylabel:
            axes.set_ylabel(ylabel, fontweight=display_settings["fontweight"])

        # Set the color of the tick labels
        axes.tick_params(colors=display_settings["label_color"], which="both")
        axes.yaxis.label.set_color(display_settings["label_color"])
        axes.xaxis.label.set_color(display_settings["label_color"])

        # Remove the top and right spines from plot
        sns.despine(right=True, top=True)

        # Set the color of the axes
        for spine in axes.spines.values():
            spine.set_edgecolor(display_settings["label_color"])

        # Add annotations for each bar
        for bar_patch in axes.patches:
            value = bar_patch.get_height()
            if value > 0:
                axes.annotate(
                    f"{value:.2f}",
                    (bar_patch.get_x() + bar_patch.get_width() / 2.0, value),
                    ha="center",
                    va="bottom",
                    fontsize=10,
                    weight=display_settings["fontweight"],
                    color=display_settings["label_color"],
                    xytext=(0, 2),
                    textcoords="offset points",
                )

        # Set the color of each bar
        lime_green = "#42cd42"
        gold = "#FFD700"
        tomato = "#FF6347"

        my_palette = [
            lime_green,
            self._get_darker_shade(lime_green),
            gold,
            self._get_darker_shade(gold),
            tomato,
            self._get_darker_shade(tomato),
        ]

        for index, bar_patch in enumerate(axes.patches):
            color_index = index % len(
                my_palette
            )  # Ensure the index loops over my_palette
            bar_patch.set_color(my_palette[color_index])

    def _plot_bar_chart(
        self, data: Dict[str, float], title: str, xlabel: str, ylabel: str
    ) -> plt.Figure:
        """
        Plots a bar chart.

        Args:
            data (Dict[str, float]): A dictionary containing the data to plot.
            title (str): The title of the plot.
            xlabel (str): The label for the x-axis.
            ylabel (str): The label for the y-axis.

        Returns:
            plt.Figure: The bar chart plot.
        """
        df = pd.DataFrame(list(data.items()), columns=["Category", "Value"])

        # for category in df["Category"]:
        #     if "unfurnished" in category:
        #         df["Category"] = df["Category"].replace(
        #             "unfurnished",
        #             Translation()["char_chart"]["column_names"]["with_no_furniture"],
        #         )
        #     elif "furnished" in category:
        #         df["Category"] = df["Category"].replace(
        #             "furnished",
        #             Translation()["char_chart"]["column_names"]["with_furniture"],
        #         )
        #     else:
        #         pass

        fig, axis = plt.subplots(figsize=self.display_settings["figsize"]["singleplot"])
        sns.barplot(
            x="Category",
            y="Value",
            data=df,
            ax=axis,
            palette=self.display_settings["palette"],
        )

        self._set_plot_aesthetics(axis, title=title, xlabel=xlabel, ylabel=ylabel)

        return fig
