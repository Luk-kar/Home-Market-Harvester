# Third-party imports
import pandas as pd
import streamlit as st

# Local imports
from model_offer_predictor import ModelPredictor


# TODO is furnished adjust to the offers
class TableVisualizer:
    def __init__(self, aesthetics=None):
        self.aesthetics = aesthetics

    def display(self, your_offers_df, other_offers_df):
        your_offers_df, offers_5km_df = self._narrow_data(
            your_offers_df, other_offers_df
        )

        self._display_title(
            "📊 Apartments Data", "Price in PLN, medians taken from 5 km radius"
        )

        df_per_flat = your_offers_df.copy()

        df_per_flat["price_by_model"] = self._add_column_calculated_price_by_model(
            your_offers_df
        )

        df_per_flat = self._add_statistical_data_to_offers(df_per_flat, offers_5km_df)

        df_per_flat = self._add_column_calculated_price_differences(
            df_per_flat, "in_5_km", "price_per_meter"
        )

        df_per_flat = self._add_column_suggested_price_by_median(df_per_flat)

        df_per_flat = self._move_column(df_per_flat, "price_percentile", 7)
        df_per_flat = self._move_column(df_per_flat, "price_by_model", 8)
        df_per_flat = self._move_column(df_per_flat, "suggested_price_by_median", 9)
        df_per_flat = self._move_column(df_per_flat, "lease_time", 14)

        df_per_flat = self._remove_unnecessary_columns(df_per_flat)

        df_per_flat = self._make_columns_titles_more_readable(df_per_flat)

        df_market_positioning = self._get_market_positioning_data(df_per_flat)

        df_owned_flats_summary = self._get_properties_summary_data(df_per_flat)

        self._display_table(df_per_flat)

        self._display_title(subtitle="Market Positioning")

        self._display_table(df_market_positioning)

    def _get_properties_summary_data(self, df_per_flat: pd.DataFrame) -> pd.Series:
        pass

    # Summary actual price total

    # Summary price total per model

    # Summary suggested price by median,

    def _add_column_calculated_price_by_model(
        self, df_per_flat: pd.DataFrame
    ) -> pd.Series:
        model_path = "notebooks\\gbm_model_file.p"
        metadata_path = "notebooks\\gbm_model_metadata.json"

        predictor = ModelPredictor(model_path, metadata_path)
        price_by_model = predictor.get_price_predictions(df_per_flat)

        price_by_model_diff = price_by_model - df_per_flat["price"]

        return price_by_model_diff

    def _add_column_suggested_price_by_median(self, df_per_flat):
        df_per_flat["suggested_price_by_median"] = df_per_flat.apply(
            lambda row: self._round_to_nearest_hundred(
                (row["in_5_km_price_per_meter"] * row["area"]) - row["price"]
            ),
            axis=1,
        )

        return df_per_flat

    def _get_market_positioning_data(self, df_per_flat):
        summary_stats = {
            "flats": len(df_per_flat["flat id"].unique()),
            "floor max": df_per_flat["floor"].max(),
            "avg area": df_per_flat["area"].mean(),
            "furnished sum": df_per_flat["is furnished"].sum(),
            "avg price": df_per_flat["price"].mean(),
            "avg price percentile": df_per_flat["price percentile"].mean(),
            "avg price by model": df_per_flat["price by model"].mean(),
            "avg suggested price by median": df_per_flat[
                "suggested price by median"
            ].mean(),
            "avg price per meter": df_per_flat["price per meter"].mean(),
            "avg price per meter difference %": df_per_flat[
                "price per meter difference %"
            ].mean(),
        }
        df_summary = pd.DataFrame([summary_stats])

        specific_columns = [
            "avg price by model",
            "avg suggested price by median",
            "price per meter difference %",
        ]

        # Custom formatting function to add '+' for positive values

        # Apply the formatting function to the specific columns
        for col in specific_columns:
            if col in df_summary.columns:
                df_summary[col] = df_summary[col].apply(self._format_with_plus_sign)

        return df_summary

    def _make_columns_titles_more_readable(self, df_per_flat):
        df_per_flat.columns = [col.replace("_", " ") for col in df_per_flat.columns]

        return df_per_flat

    def _remove_unnecessary_columns(self, df_per_flat):
        columns_to_delete = [
            "in_5_km_price",
            "in_5_km_price_per_meter",
        ]
        for column in columns_to_delete:
            del df_per_flat[column]

        return df_per_flat

    def _add_statistical_data_to_offers(self, your_offers_df, other_offers_df):
        # Create separate DataFrames for furnished and non-furnished offers
        furnished_offers = other_offers_df[
            other_offers_df["equipment"]["furniture"] == True
        ]
        non_furnished_offers = other_offers_df[
            other_offers_df["equipment"]["furniture"] == False
        ]

        # Calculate medians for furnished and non-furnished offers
        medians_furnished = {
            "price": furnished_offers["pricing"]["total_rent"].median(),
            "price_per_meter": furnished_offers["pricing"]["total_rent_sqm"].median(),
        }
        medians_non_furnished = {
            "price": non_furnished_offers["pricing"]["total_rent"].median(),
            "price_per_meter": non_furnished_offers["pricing"][
                "total_rent_sqm"
            ].median(),
        }

        # Initialize an empty DataFrame to store the median values
        medians_5km_df = pd.DataFrame(index=your_offers_df.index)

        # Iterate over rows in your_offers_df and add the corresponding medians
        for idx, row in your_offers_df.iterrows():
            if row["is_furnished"]:
                for key, value in medians_furnished.items():
                    medians_5km_df.at[idx, f"in_5_km_{key}"] = value
            else:
                for key, value in medians_non_furnished.items():
                    medians_5km_df.at[idx, f"in_5_km_{key}"] = value

        # Separate prices based on 'is_furnished' column
        furnished_prices = other_offers_df[
            other_offers_df["equipment"]["furniture"] == True
        ]["pricing"]["total_rent"]
        non_furnished_prices = other_offers_df[
            other_offers_df["equipment"]["furniture"] == False
        ]["pricing"]["total_rent"]

        # Create Series from the prices for comparison
        furnished_prices_series = pd.Series(furnished_prices.values)
        non_furnished_prices_series = pd.Series(non_furnished_prices.values)

        # Calculate percentile ranks based on 'is_furnished'
        def calculate_percentile(row):
            price = row["price"]
            is_furnished = row["is_furnished"]
            if is_furnished:
                return furnished_prices_series[
                    furnished_prices_series <= price
                ].count() / len(furnished_prices_series)
            else:
                return non_furnished_prices_series[
                    non_furnished_prices_series <= price
                ].count() / len(non_furnished_prices_series)

        your_offers_df["price_percentile"] = your_offers_df.apply(
            calculate_percentile, axis=1
        )

        # Concatenate the original DataFrame with the medians DataFrame
        df_per_flat = pd.concat([your_offers_df, medians_5km_df], axis=1)
        return df_per_flat

    def _display_title(self, text="", subtitle=""):
        st.markdown(
            f"<h3 style='text-align: center;'>{text}</h3>",
            unsafe_allow_html=True,
        )

        if subtitle:
            st.markdown(
                f"<p style='text-align: center;'>{subtitle}</p>",
                unsafe_allow_html=True,
            )

    def _narrow_data(self, your_offers_df, other_offers_df):
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
        your_offers_df = your_offers_df[selected_columns]

        offers_5km_df = other_offers_df[
            (other_offers_df["location"]["city"] == "będziński")
            | (other_offers_df["location"]["city"] == "Zawada")
        ].copy()

        return your_offers_df, offers_5km_df

    def _add_column_calculated_price_differences(
        self, df, column_prefix, base_price_per_meter_col
    ):
        # Calculate the absolute difference and percentage difference for price per meter
        price_per_meter_col = f"{column_prefix}_price_per_meter"
        if price_per_meter_col in df.columns:
            df["price per meter difference %"] = round(
                ((df[base_price_per_meter_col] / df[price_per_meter_col]) - 1) * 100, 2
            )

        return df

    def _round_to_nearest_hundred(self, number):
        return round(number / 100) * 100

    def _format_with_plus_sign(self, value):
        if pd.isna(value):
            return value
        elif isinstance(value, (float, int)) and value > 0:
            return f"+{value:.2f}"
        elif isinstance(value, (float, int)):
            return f"{value:.2f}"
        else:
            return value

    def _display_table(self, df_per_flat):
        # Define the columns where the positive values should show '+' sign
        specific_columns = [
            "price by model",
            "suggested price by median",
            "price per meter difference %",
        ]

        # Custom formatting function to add '+' for positive values

        # Apply the formatting function to the specific columns
        for col in specific_columns:
            if col in df_per_flat.columns:
                df_per_flat[col] = df_per_flat[col].apply(self._format_with_plus_sign)

        # Handle other float columns
        float_columns = df_per_flat.select_dtypes(include=["float"]).columns
        for col in float_columns:
            if col not in specific_columns:
                df_per_flat[col] = df_per_flat[col].apply(
                    lambda x: f"{x:.2f}" if pd.notna(x) else x
                )

        # Handle integer columns
        int_columns = df_per_flat.select_dtypes(include=["int"]).columns
        df_per_flat[int_columns] = df_per_flat[int_columns].astype(str)

        # Apply custom styling
        styled_df = self._style_dataframe(df_per_flat)

        # Convert DataFrame to HTML and use st.markdown to display it
        html = styled_df.to_html(escape=False)
        st.markdown(html, unsafe_allow_html=True)

    def _move_column(self, df: pd.DataFrame, column_name: str, position: int):
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

    def _style_dataframe(self, df):
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
