# Standard imports
from typing import Tuple, Optional

# Third-party imports
import pandas as pd
import streamlit as st

# Local imports
from dashboard.model_offer_predictor import ModelPredictor


# TODO is furnished adjust to the offers
class TableVisualizer:
    def __init__(self, display_settings: Optional[dict] = None):
        self.display_settings = display_settings
        self.selected_percentile: Optional[float] = None

    def display(
        self, user_apartments_df: pd.DataFrame, market_apartments_df: pd.DataFrame
    ) -> None:
        """
        Display the data in a table format.
        """

        user_apartments_narrowed, market_apartments_narrowed = self._filter_data(
            user_apartments_df, market_apartments_df
        )

        self._display_header(
            "📊 Apartments Data", "Price in PLN, medians taken from 5 km radius"
        )

        self._select_price_percentile()

        apartments_comparison_df = self._compile_apartments_data(
            user_apartments_narrowed, market_apartments_narrowed
        )

        market_positioning_df = self._compute_market_positioning_stats(
            apartments_comparison_df
        )

        property_summary_df = self._aggregate_properties_data(apartments_comparison_df)

        apartments_comparison_df = self._reorder_columns(
            apartments_comparison_df,
            {
                "price_percentile": 7,
                "price_by_model": 8,
                "percentile_based_suggested_price": 9,
                "lease_time": 14,
            },
        )

        apartments_comparison_df = self._format_column_titles(apartments_comparison_df)
        market_positioning_df = self._format_column_titles(market_positioning_df)
        property_summary_df = self._format_column_titles(property_summary_df)

        self._show_data_table(apartments_comparison_df, with_index=True)
        self._display_header(subtitle="📈 Market Positioning")
        self._show_data_table(market_positioning_df)
        self._display_header(subtitle="📋 Total Summary")
        self._show_data_table(property_summary_df)
        self._display_header(subtitle="\n\n")

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

    def _compile_apartments_data(
        self, user_apartments_df: pd.DataFrame, market_apartments_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Compile data from user apartments and market apartments into a single DataFrame.
        """

        apartments_df = user_apartments_df.copy()

        apartments_df = apartments_df.rename(columns={"price": "your_price"})

        apartments_df["price_by_model"] = self._calculate_price_by_model(apartments_df)

        apartments_df[
            "percentile_based_suggested_price"
        ] = self._calculate_percentile_based_suggested_price(
            apartments_df, market_apartments_df
        )

        apartments_df[
            "price_percentile"
        ] = self._calculate_yours_price_percentile_against_others(
            apartments_df, market_apartments_df
        )

        apartments_df[
            "price_per_meter_by_percentile"
        ] = self._calculate_price_per_meter_differences(
            apartments_df, market_apartments_df
        )

        return apartments_df

    def _compute_market_positioning_stats(
        self, apartments_comparison_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate and return market positioning data.
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
                ].apply(self._format_with_plus_sign)

        return market_positioning_summary_df

    def _aggregate_properties_data(
        self, apartments_comparison_df: pd.DataFrame
    ) -> pd.DataFrame:
        actual_price_total = apartments_comparison_df["your_price"].sum()
        """
        Aggregate and return summary data for properties.
        """

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

    def _calculate_percentile_based_suggested_price(
        self, apartments_df: pd.DataFrame, market_apartments_df: pd.DataFrame
    ) -> pd.Series:
        """
        Calculate the suggested price based on percentile for each apartment.
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
                    self.selected_percentile
                )
            else:
                sq_meter_price = non_furnished_offers["pricing"][
                    "total_rent_sqm"
                ].quantile(self.selected_percentile)

            total_price_difference = sq_meter_price * row["area"] - row["your_price"]
            return total_price_difference

        return apartments_df.apply(calculate_price, axis=1)

    def _calculate_price_by_model(self, apartments_df: pd.DataFrame) -> pd.Series:
        """
        Calculate price by model.
        """
        model_path = "notebooks\\svm_model_file.p"
        metadata_path = "notebooks\\svm_model_metadata.json"

        predictor = ModelPredictor(model_path, metadata_path)
        price_predictions = predictor.get_price_predictions(apartments_df)
        price_by_model_df = pd.Series(price_predictions)
        price_by_model_df = price_by_model_df.apply(self._round_to_nearest_hundred)

        price_by_model_diff = price_by_model_df - apartments_df["your_price"]

        return price_by_model_diff

    def _format_column_titles(self, apartments_df: pd.DataFrame) -> pd.DataFrame:
        """
        Format the column titles to be more readable.
        """

        apartments_df.columns = [col.replace("_", " ") for col in apartments_df.columns]

        return apartments_df

    def _calculate_yours_price_percentile_against_others(
        self, apartments_df: pd.DataFrame, market_apartments_df: pd.DataFrame
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

    def _calculate_percentile(
        self,
        row: pd.Series,
        furnished_prices_series: pd.Series,
        non_furnished_prices_series: pd.Series,
    ) -> float:
        """
        Calculate the percentile ranking of an apartment's price relative to market prices
        """
        price = row["your_price"]
        is_furnished = row["is_furnished"]
        if is_furnished:
            return furnished_prices_series[
                furnished_prices_series <= price
            ].count() / len(furnished_prices_series)
        else:
            return non_furnished_prices_series[
                non_furnished_prices_series <= price
            ].count() / len(non_furnished_prices_series)

    def _display_header(self, text: str = "", subtitle: str = "") -> None:
        """
        Display a formatted header.
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

    def _filter_data(
        self, user_apartments_df: pd.DataFrame, market_apartments_df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Filter the data to only include apartments that are relevant for the analysis.
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

        def filter_row(row: pd.Series) -> bool:
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

        filtered_df = market_apartments_df[
            market_apartments_df.apply(filter_row, axis=1)
        ].copy()

        user_apartments_df = user_apartments_df.rename(
            columns={"price_per_meter": "your_price_per_meter"}
        )

        return user_apartments_df, filtered_df

    def _calculate_price_per_meter_differences(
        self, apartments_df: pd.DataFrame, market_apartments_df: pd.DataFrame
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
                furnished_offers["pricing"]["total_rent_sqm"].quantile(
                    self.selected_percentile
                )
                if row["is_furnished"]
                else non_furnished_offers["pricing"]["total_rent_sqm"].quantile(
                    self.selected_percentile
                )
            )

            sq_meter_price_yours = row["your_price_per_meter"]
            percent_difference = round(
                ((sq_meter_price_others / sq_meter_price_yours) - 1) * 100, 2
            )
            return percent_difference

        return apartments_df.apply(calculate_difference, axis=1)

    def _round_to_nearest_hundred(self, number: float) -> int:
        return round(number / 100) * 100

    def _format_with_plus_sign(self, value) -> str:
        """
        Format a value with a '+' sign if it is positive.
        """
        if pd.isna(value):
            return value
        elif isinstance(value, (float, int)) and value > 0:
            return f"+{value:.2f}"
        elif isinstance(value, (float, int)):
            return f"{value:.2f}"
        else:
            return value

    def _show_data_table(self, df: pd.DataFrame, with_index: bool = False) -> None:
        """
        Display a formatted table of the DataFrame.
        """

        # Define the columns where the positive values should show '+' sign
        columns_with_plus_and_minus_at_front = [
            "price by model",
            "suggested price by percentile",
            "price per meter by percentile",
            "avg price by model",
            "avg suggested price by percentile",
            "avg price per meter by percentile",
        ]

        # Round float columns to 2 decimal places
        float_columns = df.select_dtypes(include=["float"]).columns
        for col in float_columns:
            if col not in columns_with_plus_and_minus_at_front:
                df[col] = df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else x)

        # Custom formatting function to add '+' for positive values
        # Apply the formatting function to the specific columns
        for col in columns_with_plus_and_minus_at_front:
            if col in df.columns:
                df[col] = df[col].apply(self._format_with_plus_sign)

        columns_with_percent_at_end = [
            "price per meter by percentile",
            "avg price per meter by percentile",
        ]
        # add percent sign at the end
        for col in columns_with_percent_at_end:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: f"{x}%" if pd.notna(x) else x)

        # Apply custom styling
        styled_df = self._style_dataframe(df)

        # Convert DataFrame to HTML and use st.markdown to display it
        html = styled_df.to_html(escape=False, index=with_index)
        centered_html = f"""
        <div style='display: flex; justify-content: center; align-items: center; height: 100%;'>
            <div style='text-align: center;'>{html}</div>
        </div>
        """
        st.markdown(centered_html, unsafe_allow_html=True)

    def _reorder_columns(self, df: pd.DataFrame, column_order: dict) -> pd.DataFrame:
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

    def _style_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply custom styling to a DataFrame's elements.
        """

        def apply_row_styles(row):
            for col in row.index:
                if isinstance(row[col], str) and row[col].startswith("+"):
                    row[col] = f'<span style="color: green;">{row[col]}</span>'
                elif isinstance(row[col], str) and row[col].startswith("-"):
                    row[col] = f'<span style="color: red;">{row[col]}</span>'
                elif row[col] is True:
                    row[col] = f'<span style="color: green;">True</span>'
                elif row[col] is False:
                    row[col] = f'<span style="color: red;">False</span>'
            return row

        return df.apply(apply_row_styles, axis=1)
