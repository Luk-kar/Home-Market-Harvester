"""
This module contains the English localization for the dashboard of the Home Market Harvester application.
It defines a dictionary named 'english' that contains translations for various UI elements such as 
titles, chart labels, column names, and tooltips.
"""

english = {
    "app_title": "🔍🏠 Rent comparisons",
    "char_chart": {
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
                "rent_start": "rental start",
                "id": "flat id",
                "flat_surface": "area",
                "is_furnished": "is furnished",
                "user_price": "your price",
                "percentile_price": "price percentile",
                "model_price": "price by model",
                "suggested_model_price": "percentile based suggested price",
                "user_price_per_meter": "your price per meter",
                "user_price_per_meter_percentile": "price per meter by percentile",
                "lease_time": "lease time",
            },
        },
        "market_positioning": {
            "main_title": "📈 Market Positioning",
            "column_names": {
                "flats_number": "flats",
                "max_floor": "floor max",
                "avg_flat_surface": "avg area",
                "furnished_flats_sum": "furnished_sum",
                "avg_user_price": "avg your price",
                "avg_user_percentile_price_by_market": "avg price percentile",
                "avg_price_by_model": "avg price by model",
                "avg_percentile_based_suggested_price": "avg percentile based suggested price",
                "avg_user_price_per_meter": "avg your price per meter",
                "avg_price_per_meter_suggested_by_percentile": "avg price per meter by percentile",
            },
        },
        "summary_total_calculations": {
            "main_title": "📋 Total Summary",
            "column_names": {
                "user_price_total": "avg your price",
                "by_model_price_total": "avg price percentile",
                "percentile_based_suggested_price_total": "percentile based suggested price total",
            },
        },
    },
    "map": {
        "main_title": "🗺️ Property Prices Heatmap",
        "legend_title": "Number\nof\noffers",
        "hover_tooltip": {
            "city": "City",
            "street": "Street",
            "price_total": "Total Price",
            "rent": "Rent",
            "area": "Square Meters",
            "price_per_meter": "Price/Sqm",
            "furnished": "Furnished",
        },
    },
}
