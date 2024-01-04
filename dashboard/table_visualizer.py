import pandas as pd
import streamlit as st


class TableVisualizer:
    def __init__(self, aesthetics=None):
        self.aesthetics = aesthetics

    def display(self, your_offers_df, other_offers_df):
        text = "📊 Data"
        st.markdown(
            f"<h3 style='text-align: center;'>{text}</h3>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='text-align: center;'>Price in PLN</p>", unsafe_allow_html=True
        )

        offers_5km_df = other_offers_df[
            (other_offers_df["location"]["city"] == "będziński")
            | (other_offers_df["location"]["city"] == "Zawada")
        ].copy()

        # Calculate median values for local and 20 km radius offers
        medians = {
            "in_5_km": {
                "price": offers_5km_df["pricing"]["total_rent"].median(),
                "price_per_meter": offers_5km_df["pricing"]["total_rent_sqm"].median(),
            }
        }

        # Initialize a DataFrame to store the medians with the same index as your_offers_df
        medians_df = pd.DataFrame(index=your_offers_df.index)

        # Add median values to the DataFrame
        for key, stats in medians.items():
            for stat_name, value in stats.items():
                medians_df[f"{key}_{stat_name}"] = value

        # Concatenate the original DataFrame with the medians DataFrame
        df_per_flat = pd.concat([your_offers_df, medians_df], axis=1)

        # Calculate price differences for local and in 20 km offers
        self._calculate_price_differences(df_per_flat, "in_5_km", "price_per_meter")

        df_per_flat["suggested_price_by_median"] = df_per_flat.apply(
            lambda row: self._round_to_nearest_hundred(
                row["in_5_km_price_per_meter"] * row["area"]
            ),
            axis=1,
        )

        # model suggested price TODO

        columns_to_delete = [
            "in_5_km_price",
            "in_5_km_price_per_meter",
        ]
        for column in columns_to_delete:
            del df_per_flat[column]

        # Rename all columns by replacing "_" with " "
        df_per_flat.columns = [col.replace("_", " ") for col in df_per_flat.columns]

        # Calculate summary statistics as a dictionary
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

        # Convert summary statistics dictionary to a DataFrame
        df_summary = pd.DataFrame([summary_stats])

        self._display_table_per_flat(df_per_flat)

        # Display the DataFrame in Streamlit
        self._display_table_per_flat(df_summary)

    def _calculate_price_differences(self, df, column_prefix, base_price_per_meter_col):
        # Calculate the absolute difference and percentage difference for price per meter
        price_per_meter_col = f"{column_prefix}_price_per_meter"
        if price_per_meter_col in df.columns:
            df[f"{column_prefix}_price_difference_%"] = round(
                ((df[base_price_per_meter_col] / df[price_per_meter_col]) - 1) * 100, 2
            )

    def _round_to_nearest_hundred(self, number):
        return round(number / 100) * 100

    def _display_table_per_flat(self, df_per_flat):
        float_columns = df_per_flat.select_dtypes(include=["float", "int"]).columns
        df_per_flat[float_columns] = df_per_flat[float_columns].applymap(
            lambda x: f"{x:.2f}"
        )

        st.table(df_per_flat)
