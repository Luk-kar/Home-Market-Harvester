"""
This module contains the English localization for the dashboard of the Home Market Harvester application.
It defines a dictionary named 'english' that contains translations for various UI elements such as 
titles, chart labels, column names, and tooltips.
"""

english = {
    "app_title": "🔍🏠 Rent comparisons",
    "bar_chart": {
        "main_title": "⚖️ Median Price",
        "charts_titles": {
            "price_per_meter": "Price per meter",
            "price_per_offer": "Price per offer",
        },
        "x_axis_price": "Price (PLN)",
        "y_axis_offers": {
            "yours": "Yours",
            "like_yours": "Similar",
            "all": "All in 20 km radius",
        },
        "column_names": {
            "with_furniture": "furnished",
            "with_no_furniture": "unfurnished",
        },
    },
    "table": {
        "main_title": "📊 Your flats",
        "subtitle": "Price in PLN, medians taken from similar nearby offers",
        "apartments": {
            "percentile_dropdown": "Select Percentile for Suggested Price Calculation",
            "column_names": {
                "rental_start": "rent start",
                "flat_id": "flat_id",
                "floor": "floor",
                "number_of_rooms": "number of rooms",
                "area": "area",
                "is_furnished": "is furnished",
                "your_price": "your price",
                "price_percentile": "price percentile",
                "price_by_model": "price by model",
                "percentile_based_suggested_price": "percentile based suggested price",
                "your_price_per_meter": "your price per meter",
                "price_per_meter_by_percentile": "price per meter by percentile",
                "lease_time": "lease time",
            },
            "column_values": {
                "boolean": {
                    "True": "yes",
                    "False": "no",
                },
                # The order of the keys in the dictionary below is important.
                "time_intervals": {
                    "nan": "-",
                    "days": "days",
                    "day": "day",
                    "weeks": "weeks",
                    "week": "week",
                    "months": "months",
                    "month": "month",
                    "years": "years",
                    "year": "year",
                },
            },
        },
        "market_positioning": {
            "main_title": "📈 Market Positioning",
            "column_names": {
                "flats": "flats",
                "floor_max": "floor max",
                "avg_area": "avg area",
                "furnished_sum": "furnished_sum",
                "avg_your_price": "avg your price",
                "avg_price_percentile": "avg price percentile",
                "avg_price_by_model": "avg price by model",
                "avg_percentile_based_suggested_price": "avg percentile based suggested price",
                "avg_your_price_per_meter": "avg your price per meter",
                "avg_price_per_meter_by_percentile": "avg price per meter by percentile",
            },
        },
        "summary_total_calculations": {
            "main_title": "📋 Total Summary",
            "column_names": {
                "your_price_total": "your price total",
                "price_total_per_model": "price total per model",
                "percentile_based_suggested_price_total": "percentile based suggested price total",
            },
        },
    },
    "map": {
        "main_title": "🗺️ Property Prices Heatmap",
        "legend_title": "Number<br>of<br>offers",
        "hover_tooltip": {
            "city": "City",
            "street": "Street",
            "price_total": "Total Price",
            "price": "Price",
            "rent": "Rent",
            "area": "Square Meters",
            "price_per_meter": "Price/Sqm",
            "furnished": "Furnished",
            "boolean": {
                True: "yes",
                False: "no",
            },
            "nan": "-",
        },
    },
}
