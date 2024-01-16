# Standard imports
from typing import Any, Dict, List, Optional, Tuple, Union

# Third-party imports
import matplotlib.axes._axes as Axes
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st


class BarChartVisualizer:
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
        self.bar_chart_title = bar_chart_title

        """
        Initializes the bar chart visualizer with necessary data.
        """

    def display(self) -> None:
        if self.bar_chart_title:
            st.markdown(
                f"<h3 style='text-align: center;'>{self.bar_chart_title}</h3>",
                unsafe_allow_html=True,
            )

        offers = self._create_offers_dict()

        price_per_meter_col, price_per_offer_col = st.columns(2)

        categories = ["Yours", "Similar", "All in 20 km radius"]

        xlabel = self._generate_x_label(categories)
        ylabel = "Price (PLN)"

        with price_per_meter_col:
            per_meter_data = self._calculate_median_data(offers, "price_per_meter")
            st.pyplot(
                self._plot_bar_chart(
                    per_meter_data,
                    "Price per meter",
                    xlabel,
                    ylabel,
                )
            )

        with price_per_offer_col:
            per_offer_data = self._calculate_median_data(offers, "price")
            st.pyplot(
                self._plot_bar_chart(
                    per_offer_data,
                    "Price per offer",
                    xlabel,
                    ylabel,
                )
            )

    def _filter_row(row: pd.Series) -> bool:
        """
        Filter rows based on the following criteria:
        - City is in the list of cities
        - Building type is in the list of building types
        - Build year is less than or equal to 1970
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

    def _generate_x_label(self, categories: List[str]) -> str:
        space = " " * 36
        max_length = max(len(category) for category in categories)
        centered_categories = [category.center(max_length) for category in categories]
        return space.join(centered_categories)

    def _calculate_median_data(
        self, offers: Dict[str, Dict[str, pd.DataFrame]], column: str
    ) -> Dict[str, float]:
        """
        Calculates the median price per meter for each offer category.
        """
        additional_spacing = {
            "Yours": -1,
            "Similar": None,
            "All in 20 km radius": 0,
        }

        column_mappings = {
            "price": ("price", ("pricing", "total_rent")),
            "price_per_meter": ("price_per_meter", ("pricing", "total_rent_sqm")),
        }

        data = {}

        for category, furnishings in offers.items():
            for furniture, df in furnishings.items():
                primary_col, fallback_col = column_mappings[column]
                price_column = (
                    primary_col if primary_col in df.columns else fallback_col
                )

                median = df[price_column].median().round(2)

                position_to_add_space = additional_spacing[category]
                column_name = self._format_column_name_for_display(
                    furniture, position_to_add_space
                )

                data[column_name] = median

        return data

    def _format_column_name_for_display(
        self, furniture: str, position_to_add_space: Optional[int]
    ) -> str:
        """
        This method provides a clever workaround to create visually similar names
        for bar chart columns by strategically inserting spaces at various positions along the edges of the names.
        While the resulting strings are technically different, they appear identical when displayed.
        This approach ensures that column names remain distinct and are not inadvertently overwritten.

        """
        return (
            self._insert_char(furniture, position_to_add_space, " ")
            if position_to_add_space is not None
            else furniture
        )

    def _insert_char(
        self, original_string: str, position: int, char_to_insert: str
    ) -> str:
        """
        Inserts a character at the specified position in a string.
        """

        if position < 0:
            position = len(original_string) + position + 1
        elif position >= len(original_string):
            raise Exception("Position is out of range.")
        elif position < 0 and abs(position) > len(original_string):
            raise Exception("Position is out of range.")

        return original_string[:position] + char_to_insert + original_string[position:]

    def _create_offers_dict(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Creates a dictionary of offers for each category.
        """
        # TODO add local market
        return {
            "Yours": {
                "furnished": self.user_apartments_df[
                    self.user_apartments_df["is_furnished"] == True
                ],
                "unfurnished": self.user_apartments_df[
                    self.user_apartments_df["is_furnished"] == False
                ],
            },
            "Similar": {
                "furnished": self.market_apartments_df[
                    (self.market_apartments_df["equipment"]["furniture"] == True)
                    & (self.market_apartments_df["location"]["city"] == "będziński")
                ],
                "unfurnished": self.market_apartments_df[
                    (self.market_apartments_df["equipment"]["furniture"] == False)
                    & (self.market_apartments_df["location"]["city"] == "będziński")
                ],
            },
            "All in 20 km radius": {
                "furnished": self.market_apartments_df[
                    self.market_apartments_df["equipment"]["furniture"] == True
                ],
                "unfurnished": self.market_apartments_df[
                    self.market_apartments_df["equipment"]["furniture"] == False
                ],
            },
        }

    def _get_darker_shade(self, color: str, factor: float = 0.5) -> str:
        """
        Darkens a color by a specified factor.
        """
        rgb = mcolors.hex2color(color)
        darkened_rgb = [max(0, c * factor) for c in rgb]
        darkened_hex = mcolors.rgb2hex(darkened_rgb)
        return darkened_hex

    def _set_plot_aesthetics(
        self,
        ax: Axes,
        title: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
    ) -> None:
        """
        Sets the aesthetics of the plot.
        """

        display_settings = self.display_settings

        # Set the title and axis labels
        if title:
            ax.set_title(
                title,
                color=display_settings["label_color"],
                fontweight=display_settings["fontweight"],
            )
        if xlabel:
            ax.set_xlabel(xlabel, fontweight=display_settings["fontweight"])
        if ylabel:
            ax.set_ylabel(ylabel, fontweight=display_settings["fontweight"])

        # Set the color of the tick labels
        ax.tick_params(colors=display_settings["label_color"], which="both")
        ax.yaxis.label.set_color(display_settings["label_color"])
        ax.xaxis.label.set_color(display_settings["label_color"])

        # Remove the top and right spines from plot
        sns.despine(right=True, top=True)

        # Set the color of the axes
        for spine in ax.spines.values():
            spine.set_edgecolor(display_settings["label_color"])

        # Add annotations for each bar
        for p in ax.patches:
            value = p.get_height()
            if value > 0:
                ax.annotate(
                    f"{value:.2f}",
                    (p.get_x() + p.get_width() / 2.0, value),
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

        for index, p in enumerate(ax.patches):
            color_index = index % len(
                my_palette
            )  # Ensure the index loops over my_palette
            p.set_color(my_palette[color_index])

    def _plot_bar_chart(
        self, data: Dict[str, float], title: str, xlabel: str, ylabel: str
    ) -> plt.Figure:
        df = pd.DataFrame(list(data.items()), columns=["Category", "Value"])
        fig, ax = plt.subplots(figsize=self.display_settings["figsize"]["singleplot"])
        sns.barplot(
            x="Category",
            y="Value",
            data=df,
            ax=ax,
            palette=self.display_settings["palette"],
        )

        self._set_plot_aesthetics(ax, title=title, xlabel=xlabel, ylabel=ylabel)

        return fig
