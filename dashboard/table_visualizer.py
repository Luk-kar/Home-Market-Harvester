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

        self._display_title()

        df_per_flat = your_offers_df.copy()

        df_per_flat["price_by_model"] = self._add_column_calculated_price_by_model(
            your_offers_df
        )

        df_per_flat = self.move_column(df_per_flat, "price_by_model", 7)

        df_per_flat = self._add_statistical_data_to_offers(df_per_flat, offers_5km_df)

        df_per_flat = self._add_column_calculated_price_differences(
            df_per_flat, "in_5_km", "price_per_meter"
        )

        df_per_flat = self._add_column_suggested_price_by_median(df_per_flat)

        df_per_flat = self.move_column(df_per_flat, "suggested_price_by_median", 8)

        df_per_flat = self._remove_unnecessary_columns(df_per_flat)

        df_per_flat = self._make_columns_titles_more_readable(df_per_flat)

        df_summary = self._get_summary_data(df_per_flat)

        self._display_table(df_per_flat)

        self._display_table(df_summary)

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

    def _get_summary_data(self, df_per_flat):
        summary_stats = {
            "flats": len(df_per_flat["flat id"].unique()),
            "floor max": df_per_flat["floor"].max(),
            "avg area": df_per_flat["area"].mean(),
            "furnished sum": df_per_flat["is furnished"].sum(),
            "avg price": df_per_flat["price"].mean(),
            "avg price per meter": df_per_flat["price per meter"].mean(),
            "avg in 5 km price difference %": df_per_flat[
                "in 5 km price difference %"
            ].mean(),
            "avg suggested price by median": df_per_flat[
                "suggested price by median"
            ].mean(),
        }
        df_summary = pd.DataFrame([summary_stats])
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

    def _display_title(self):
        text = "📊 Apartments Data"
        st.markdown(
            f"<h3 style='text-align: center;'>{text}</h3>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='text-align: center;'>Price in PLN</p>", unsafe_allow_html=True
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
            df[f"{column_prefix}_price_difference_%"] = round(
                ((df[base_price_per_meter_col] / df[price_per_meter_col]) - 1) * 100, 2
            )

        return df

    def _round_to_nearest_hundred(self, number):
        return round(number / 100) * 100

    def _display_table(self, df_per_flat):
        float_columns = df_per_flat.select_dtypes(include=["float"]).columns
        df_per_flat[float_columns] = df_per_flat[float_columns].applymap(
            lambda x: f"{x:.2f}"
        )

        st.table(df_per_flat)

    def move_column(self, df: pd.DataFrame, column_name: str, position: int):
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
