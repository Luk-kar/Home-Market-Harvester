# Standard imports
from typing import Tuple, Optional

# Third-party imports
import pandas as pd
import streamlit as st

# Local imports
from model_offer_predictor import ModelPredictor


# TODO is furnished adjust to the offers
class TableVisualizer:
    def __init__(self, display_settings: Optional[dict] = None):
        self.display_settings = display_settings
        self.selected_percentile: Optional[float] = None

    def display(
        self, user_apartments_df: pd.DataFrame, market_apartments_df: pd.DataFrame
    ) -> None:
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

        market_positioning_df = self._calculate_market_positioning(
            apartments_comparison_df
        )

        property_summary_df = self._aggregate_properties_data(apartments_comparison_df)

        apartments_comparison_df = self._move_column(
            apartments_comparison_df, "price_percentile", 7
        )
        apartments_comparison_df = self._move_column(
            apartments_comparison_df, "price_by_model", 8
        )
        apartments_comparison_df = self._move_column(
            apartments_comparison_df, "suggested_price_by_percentile", 9
        )
        apartments_comparison_df = self._move_column(
            apartments_comparison_df, "lease_time", 14
        )

        apartments_comparison_df = self._format_column_titles(apartments_comparison_df)
        market_positioning_df = self._format_column_titles(market_positioning_df)
        property_summary_df = self._format_column_titles(property_summary_df)

        self._show_data_table(apartments_comparison_df, show_index=True)
        self._display_header(subtitle="📈 Market Positioning")
        self._show_data_table(market_positioning_df)
        self._display_header(subtitle="📋 Total Summary")
        self._show_data_table(property_summary_df)
        self._display_header(subtitle="\n\n")

    def _select_price_percentile(self) -> None:
        # Using st.columns to set the width of st.selectbox

        col1, col2, col3 = st.columns([1, 1, 1])

        with col2:  # Adjust the column index and width ratio as needed
            self.selected_percentile = st.selectbox(
                "Select Percentile for Suggested Price Calculation",
                options=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                index=4,  # Default to 0.5
            )

    def _compile_apartments_data(
        self, user_apartments_df: pd.DataFrame, offers_other_df: pd.DataFrame
    ) -> pd.DataFrame:
        df_apartments = user_apartments_df.copy()

        df_apartments = df_apartments.rename(columns={"price": "your_price"})

        df_apartments["price_by_model"] = self._calculate_price_by_model(df_apartments)

        df_apartments["suggested_price_by_percentile"] = df_apartments.apply(
            lambda row: self._calculate_suggested_price_by_percentile(
                row, offers_other_df, self.selected_percentile
            ),
            axis=1,
        )

        df_apartments[
            "price_percentile"
        ] = self._calculate_yours_price_percentile_against_others(
            df_apartments, offers_other_df
        )

        df_apartments["price_per_meter_by_percentile"] = df_apartments.apply(
            lambda row: self._calculate_price_per_meter_differences(
                row, offers_other_df, self.selected_percentile
            ),
            axis=1,
        )

        return df_apartments

    def _aggregate_properties_data(self, df_apartments: pd.DataFrame) -> pd.DataFrame:
        actual_price_total = df_apartments["your_price"].sum()

        price_total_per_model = (
            actual_price_total + df_apartments["price_by_model"].sum()
        )  # price by model is additional sum

        suggested_price_by_percentile_total = (
            actual_price_total + df_apartments["suggested_price_by_percentile"].sum()
        )  # price by median is additional sum

        summary_data = pd.DataFrame(
            {
                "your_price_total": [actual_price_total],
                "price_total_per_model": [price_total_per_model],
                "suggested_price_by_percentile_total": [
                    suggested_price_by_percentile_total
                ],
            }
        )

        return summary_data

    def _calculate_suggested_price_by_percentile(
        self, row: pd.Series, market_apartments_df: pd.DataFrame, percentile: float
    ) -> float:
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

    def _calculate_price_by_model(self, df_apartments: pd.DataFrame) -> pd.Series:
        model_path = "notebooks\\svm_model_file.p"
        metadata_path = "notebooks\\svm_model_metadata.json"

        predictor = ModelPredictor(model_path, metadata_path)
        price_predictions = predictor.get_price_predictions(df_apartments)
        price_by_model = pd.Series(price_predictions)
        price_by_model = price_by_model.apply(self._round_to_nearest_hundred)

        price_by_model_diff = price_by_model - df_apartments["your_price"]

        return price_by_model_diff

    def _add_column_suggested_price_by_median(
        self, df_apartments: pd.DataFrame
    ) -> pd.DataFrame:
        df_apartments["suggested_price_by_median"] = df_apartments.apply(
            lambda row: self._round_to_nearest_hundred(
                (row["in_5_km_price_per_meter"] * row["area"]) - row["your_price"]
            ),
            axis=1,
        )

        return df_apartments

    def _calculate_market_positioning(
        self, df_apartments: pd.DataFrame
    ) -> pd.DataFrame:
        summary_stats = {
            "flats": len(df_apartments["flat_id"].unique()),
            "floor_max": df_apartments["floor"].max(),
            "avg_area": df_apartments["area"].mean(),
            "furnished_sum": df_apartments["is_furnished"].sum(),
            "avg_your_price": df_apartments["your_price"].mean(),
            "avg_price_percentile": df_apartments["price_percentile"].mean(),
            "avg_price_by_model": df_apartments["price_by_model"].mean(),
            "avg_suggested_price_by_percentile": df_apartments[
                "suggested_price_by_percentile"
            ].mean(),
            "avg_your_price_per_meter": df_apartments["your_price_per_meter"].mean(),
            "avg_price_per_meter_by_percentile": df_apartments[
                "price_per_meter_by_percentile"
            ].mean(),
        }
        df_summary = pd.DataFrame([summary_stats])

        specific_columns = [
            "avg_price_by_model",
            "avg_suggested_price_by_median",
            "price_per_meter_by_percentile",
        ]

        # Custom formatting function to add '+' for positive values

        # Apply the formatting function to the specific columns
        for col in specific_columns:
            if col in df_summary.columns:
                df_summary[col] = df_summary[col].apply(self._format_with_plus_sign)

        return df_summary

    def _format_column_titles(self, df_apartments: pd.DataFrame) -> pd.DataFrame:
        df_apartments.columns = [col.replace("_", " ") for col in df_apartments.columns]

        return df_apartments

    def _calculate_yours_price_percentile_against_others(
        self, user_apartments_df: pd.DataFrame, market_apartments_df: pd.DataFrame
    ) -> pd.Series:
        # Separate prices based on 'is_furnished' column
        furnished_prices = market_apartments_df[
            market_apartments_df["equipment"]["furniture"] == True
        ]["pricing"]["total_rent"]
        non_furnished_prices = market_apartments_df[
            market_apartments_df["equipment"]["furniture"] == False
        ]["pricing"]["total_rent"]

        # Create Series from the prices for comparison
        furnished_prices_series = pd.Series(furnished_prices.values)
        non_furnished_prices_series = pd.Series(non_furnished_prices.values)

        # Calculate percentile ranks based on 'is_furnished'
        your_price_as_percentile_of_other_offers = user_apartments_df.apply(
            lambda row: self._calculate_percentile(
                row, furnished_prices_series, non_furnished_prices_series
            ),
            axis=1,
        )

        return your_price_as_percentile_of_other_offers

    def _calculate_percentile(
        self,
        row: pd.Series,
        furnished_prices_series: pd.Series,
        non_furnished_prices_series: pd.Series,
    ) -> float:
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

        narrowed_df = market_apartments_df[
            market_apartments_df.apply(filter_row, axis=1)
        ].copy()

        user_apartments_df = user_apartments_df.rename(
            columns={"price_per_meter": "your_price_per_meter"}
        )

        return user_apartments_df, narrowed_df

    def _calculate_price_per_meter_differences(
        self, row: pd.Series, offers_others_df: pd.DataFrame, percentile: float
    ) -> float:
        furnished_offers = offers_others_df[
            offers_others_df["equipment"]["furniture"] == True
        ]
        non_furnished_offers = offers_others_df[
            offers_others_df["equipment"]["furniture"] == False
        ]

        sq_meter_price_others = None
        if row["is_furnished"]:
            sq_meter_price_others = furnished_offers["pricing"][
                "total_rent_sqm"
            ].quantile(percentile)
        else:
            sq_meter_price_others = non_furnished_offers["pricing"][
                "total_rent_sqm"
            ].quantile(percentile)

        sq_meter_price_yours = row["your_price_per_meter"]

        percent_difference = round(
            ((sq_meter_price_others / sq_meter_price_yours) - 1) * 100, 2
        )

        return percent_difference

    def _round_to_nearest_hundred(self, number: float) -> int:
        return round(number / 100) * 100

    def _format_with_plus_sign(self, value) -> str:
        if pd.isna(value):
            return value
        elif isinstance(value, (float, int)) and value > 0:
            return f"+{value:.2f}"
        elif isinstance(value, (float, int)):
            return f"{value:.2f}"
        else:
            return value

    def _show_data_table(self, df: pd.DataFrame, show_index: bool = False) -> None:
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
        html = styled_df.to_html(escape=False, index=show_index)
        centered_html = f"""
        <div style='display: flex; justify-content: center; align-items: center; height: 100%;'>
            <div style='text-align: center;'>{html}</div>
        </div>
        """
        st.markdown(centered_html, unsafe_allow_html=True)

    def _move_column(
        self, df: pd.DataFrame, column_name: str, position: int
    ) -> pd.DataFrame:
        """
        Move a column in the DataFrame to a specified position.

        Args:
            df (pd.DataFrame): The DataFrame to modify.
            column_name (str): The name of the column to move.
            position (int): The new position for the column (0-indexed).

        Returns:
            pd.DataFrame: The DataFrame with the column moved to the new position.
        """
        columns = list(df.columns)
        if column_name in columns:
            columns.insert(position, columns.pop(columns.index(column_name)))
            return df[columns]
        else:
            print(f"Column '{column_name}' not found in DataFrame.")
            return df

    def _style_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
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
