"""
This module contains the Polish localization for the dashboard of the Home Market Harvester application.
It defines a dictionary named 'polish' that contains translations for various UI elements such as 
titles, chart labels, column names, and tooltips.
"""

polish = {
    "app_title": "🔍🏠 Porównanie Wynajmu",
    "char_chart": {
        "main_title": "⚖️ Średnia Cena",
        "charts_titles": {
            "price_per_meter": "Cena za metr",
            "price_per_offer": "Cena za ofertę",
        },
        "x_axis_price": "Cena (PLN)",
        "y_axis_offers": {
            "yours": "Twoja oferta",
            "like_yours": "Podobne",
            "all": "W promieniu 20 km",
        },
        "column_names": {
            "with_furniture": "umeblowane",
            "with_no_furniture": "nieumeblowane",
        },
    },
    "table": {
        "main_title": "📊 Twoje Mieszkania",
        "subtitle": "Ceny w PLN, mediany pochadzą z podobnych, pobliskich ofert",
        "apartments": {
            "percentile_dropdown": "Wybierz Percentyl by sklakulować sugerowaną cenę",
            "column_names": {
                "rent_start": "wynajem od",
                "id": "numer mieszkania",
                "flat_surface": "powierzchnia",
                "is_furnished": "umeblowane",
                "user_price": "twoja cena",
                "percentile_price": "percentyl ceny",
                "model_price": "cena według modelu",
                "suggested_model_price": "sugerowana cena na podstawie percentyla",
                "user_price_per_meter": "twoja cena za metr",
                "user_price_per_meter_percentile": "cena za metr według percentyla",
                "lease_time": "czas wynajmu",
            },
        },
        "market_positioning": {
            "column_names": {
                "flats_number": "liczba mieszkań",
                "max_floor": "maksymalne piętro",
                "avg_flat_surface": "średnia powierzchnia",
                "furnished_flats_sum": "ilość umeblowanych mieszkań",
                "avg_user_price": "średnia twoja cena",
                "avg_user_percentile_price_by_market": "średnia cena percentylowa",
                "avg_price_by_model": "średnia cena według modelu",
                "avg_percentile_based_suggested_price": "średnia sugerowana cena na podstawie percentyla",
                "avg_user_price_per_meter": "średnia twoja cena za metr",
                "avg_price_per_meter_suggested_by_percentile": "średnia cena za metr według percentyla",
            },
        },
        "summary_total_calculations": {
            "column_names": {
                "user_price_total": "suma twoich cen",
                "by_model_price_total": "suma cen wg modelu",
                "percentile_based_suggested_price_total": "suma sugerowanych cen na podstawie percentyla",
            },
        },
    },
    "map": {
        "main_title": "🗺️ Mapa cieplna nieruchomości",
        "legend_title": "Liczba\noffert",
        "hover_tooltip": {
            "city": "Miasto",
            "street": "Ulica",
            "price_total": "Cena całkowita",
            "rent": "Zawarty czynsz",
            "area": "Metry kwadratowe",
            "price_per_meter": "Cena za metr",
            "furnished": "Umeblowane",
        },
    },
}
