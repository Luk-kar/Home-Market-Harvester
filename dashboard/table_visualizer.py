import pandas as pd
import streamlit as st


class TableVisualizer:
    def __init__(self, aesthetics=None):
        self.aesthetics = aesthetics

    def display(self, your_offers_df, other_offers_df):
        your_offers_df, offers_5km_df = self._narrow_data(
            your_offers_df, other_offers_df
        )

        self._display_title()

        df_per_flat = self.add_statistical_data_to_offers(your_offers_df, offers_5km_df)

        df_per_flat = self._add_column_calculated_price_differences(
            df_per_flat, "in_5_km", "price_per_meter"
        )

        df_per_flat = self._add_column_suggested_price_by_median(df_per_flat)

        # model suggested price TODO

        df_per_flat = self.remove_unnecessary_columns(df_per_flat)

        df_per_flat = self.make_columns_titles_more_readable(df_per_flat)

        df_summary = self.get_summary_data(df_per_flat)

        self._display_table(df_per_flat)

        self._display_table(df_summary)

    def _add_column_suggested_price_by_median(self, df_per_flat):
        df_per_flat["suggested_price_by_median"] = df_per_flat.apply(
            lambda row: self._round_to_nearest_hundred(
                row["in_5_km_price_per_meter"] * row["area"]
            ),
            axis=1,
        )
        return df_per_flat

    def get_summary_data(self, df_per_flat):
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

    def make_columns_titles_more_readable(self, df_per_flat):
        df_per_flat.columns = [col.replace("_", " ") for col in df_per_flat.columns]

        return df_per_flat

    def remove_unnecessary_columns(self, df_per_flat):
        columns_to_delete = [
            "in_5_km_price",
            "in_5_km_price_per_meter",
        ]
        for column in columns_to_delete:
            del df_per_flat[column]

        return df_per_flat

    def add_statistical_data_to_offers(self, your_offers_df, offers_5km_df):
        medians_5km = {
            "in_5_km": {
                "price": offers_5km_df["pricing"]["total_rent"].median(),
                "price_per_meter": offers_5km_df["pricing"]["total_rent_sqm"].median(),
            }
        }

        medians_5km_df = pd.DataFrame(index=your_offers_df.index)

        # Add median values to the DataFrame
        for key, stats in medians_5km.items():
            for stat_name, value in stats.items():
                medians_5km_df[f"{key}_{stat_name}"] = value

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
            "deposit",
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
