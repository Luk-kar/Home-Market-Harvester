# Third-party imports
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st


class BarChartVisualizer:
    def __init__(
        self,
        display_settings,
        user_apartments_df,
        market_apartments_df,
        bar_chart_title,
    ):
        self.display_settings = display_settings
        self.user_apartments_df = user_apartments_df
        self.market_apartments_df = market_apartments_df
        self.bar_chart_title = bar_chart_title

    def display(self):  # TODO
        if self.bar_chart_title:
            st.markdown(
                f"<h3 style='text-align: center;'>{self.bar_chart_title}</h3>",
                unsafe_allow_html=True,
            )

        offers = {
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

        col_per_meter, col_per_offer = st.columns(2)

        space = " " * 36
        categories = ["Yours", "Similar", "All in 20 km radius"]

        max_length = max(len(category) for category in categories)
        centered_categories = [category.center(max_length) for category in categories]

        xlabel = space.join(centered_categories)
        ylabel = "Price (PLN)"

        with col_per_meter:
            per_meter_data = {
                "furnished ": offers["Yours"]["furnished"]["price_per_meter"].median(),
                "unfurnished ": offers["Yours"]["unfurnished"][
                    "price_per_meter"
                ].median(),
                "furnished": round(
                    offers["Similar"]["furnished"]["pricing"][
                        "total_rent_sqm"
                    ].median(),
                    2,
                ),
                "unfurnished": round(
                    offers["Similar"]["unfurnished"]["pricing"][
                        "total_rent_sqm"
                    ].median(),
                    2,
                ),
                " furnished": round(
                    offers["All in 20 km radius"]["furnished"]["pricing"][
                        "total_rent_sqm"
                    ].median(),
                    2,
                ),
                " unfurnished": round(
                    offers["All in 20 km radius"]["unfurnished"]["pricing"][
                        "total_rent_sqm"
                    ].median(),
                    2,
                ),
            }
            st.pyplot(
                self._plot_bar_chart(
                    per_meter_data,
                    "Price per meter",
                    xlabel,
                    ylabel,
                )
            )

        with col_per_offer:
            per_offer_data = {
                "furnished ": offers["Yours"]["furnished"]["price"].median(),
                "unfurnished ": offers["Yours"]["unfurnished"]["price"].median(),
                "furnished": round(
                    offers["Similar"]["furnished"]["pricing"]["total_rent"].median(),
                    2,
                ),
                "unfurnished": round(
                    offers["Similar"]["unfurnished"]["pricing"]["total_rent"].median(),
                    2,
                ),
                " furnished": round(
                    offers["All in 20 km radius"]["furnished"]["pricing"][
                        "total_rent"
                    ].median(),
                    2,
                ),
                " unfurnished": round(
                    offers["All in 20 km radius"]["unfurnished"]["pricing"][
                        "total_rent"
                    ].median(),
                    2,
                ),
            }
            st.pyplot(
                self._plot_bar_chart(
                    per_offer_data,
                    "Price per offer",
                    xlabel,
                    ylabel,
                )
            )

    def _get_darker_shade(self, color, factor=0.5):
        rgb = mcolors.hex2color(color)
        darkened_rgb = [max(0, c * factor) for c in rgb]
        darkened_hex = mcolors.rgb2hex(darkened_rgb)
        return darkened_hex

    def _set_plot_aesthetics(self, ax, title=None, xlabel=None, ylabel=None):
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

    def _plot_bar_chart(self, data, title, xlabel, ylabel):
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
