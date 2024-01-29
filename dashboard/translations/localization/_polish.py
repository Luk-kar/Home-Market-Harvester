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
            "percentile_dropdown": "Wybierz percentyl by wyliczyć sugerowaną cenę",
            "column_names": {
                "rental_start": "wynajem od",
                "flat_id": "numer mieszkania",
                "floor": "piętro",
                "number_of_rooms": "liczba pokoi",
                "area": "powierzchnia",
                "is_furnished": "umeblowane",
                "your_price": "twoja cena",
                "price_percentile": "percentyl ceny",
                "price_by_model": "cena według modelu",
                "percentile_based_suggested_price": "sugerowana cena na podstawie percentyla",
                "your_price_per_meter": "twoja cena za metr",
                "price_per_meter_by_percentile": "cena za metr według percentyla",
                "lease_time": "czas wynajmu",
            },
            "column_values": {
                "boolean": {
                    "True": "tak",
                    "False": "nie",
                },
                # The order of the keys in the dictionary below is important.
                # Well Polish grammar is much more complex than that but it works in most cases.
                # Mostly due to the fact of declination of nouns.
                # https://rhapsodyinlingo.com/en/polish-numbers/
                "time_intervals": {
                    "nan": "-",
                    "days": "dni",
                    "day": "dzień",
                    "weeks": "tygodni",
                    "week": "tydzień",
                    "months": "miesięcy",
                    "month": "miesiąc",
                    "years": "lat",
                    "year": "rok",
                },
            },
        },
        "market_positioning": {
            "main_title": "📊 Pozycjonowanie na rynku",
            "column_names": {
                "flats": "liczba mieszkań",
                "floor_max": "maksymalne piętro",
                "avg_area": "średnia powierzchnia",
                "furnished_sum": "ilość umeblowanych mieszkań",
                "avg_your_price": "średnia twoja cena",
                "avg_price_percentile": "średnia cena percentylowa",
                "avg_price_by_model": "średnia cena według modelu",
                "avg_percentile_based_suggested_price": "średnia sugerowana cena na podstawie percentyla",
                "avg_your_price_per_meter": "średnia twoja cena za metr",
                "avg_price_per_meter_by_percentile": "średnia cena za metr według percentyla",
            },
        },
        "summary_total_calculations": {
            "main_title": "📊 Podsumowanie",
            "column_names": {
                "your_price_total": "suma twoich cen",
                "price_total_per_model": "suma cen wg modelu",
                "percentile_based_suggested_price_total": "suma sugerowanych cen na podstawie percentyla",
            },
        },
    },
    "map": {
        "main_title": "🗺️ Mapa cieplna nieruchomości",
        "legend_title": "Liczba<br>offert",
        "hover_tooltip": {
            "city": "Miasto",
            "street": "Ulica",
            "price_total": "Cena całkowita",
            "price": "Cena",
            "rent": "Zawarty czynsz",
            "area": "Metry kwadratowe",
            "price_per_meter": "Cena za metr",
            "furnished": "Umeblowane",
            "boolean": {
                True: "tak",
                False: "nie",
            },
            "nan": "-",
        },
    },
}
