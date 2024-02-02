"""
This module contains the MapVisualizer class, 
which is used to display map visualizations using Plotly and Scattermapbox.
"""

# Third-party imports
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Local imports
from pipeline.src.dashboard.translations.translation_manager import Translation


class MapVisualizer:
    """
    A class used to display map visualizations using Plotly and Scattermapbox.

    Args:
        display_settings (dict): The display settings for the dashboard.

    Methods:
        display: Display a map visualization using Plotly and Scattermapbox.
    """

    def __init__(self, display_settings):
        self.display_settings = display_settings
        self.texts = Translation()["map"]
        self.legend_title = f"{self.texts['legend_title']}:"

    def display(
        self,
        map_df: pd.DataFrame,
        title: str = "",
        center_coords: tuple[float, float] = None,
        center_marker_name: str = "Default",
        zoom: float = 10.0,
    ):
        """
        Display a map visualization using Plotly and Scattermapbox.

        Args:
            map_df (pd.DataFrame): DataFrame containing map data.
            title (str, optional): Title for the map visualization. Defaults to "".
            center_coords (tuple[float, float], optional): Coordinates for the center of the map.
                                                           Defaults to None.
            center_marker_name (str, optional): Name for the center marker. Defaults to "Default".
            zoom (float, optional): Zoom level of the map. Defaults to 10.0.
        """

        # Extract latitude and longitude from 'coords' column in map_df
        map_df["Latitude"], map_df["Longitude"] = zip(
            *map_df["coords"].apply(self._extract_lat_lon)
        )

        # Round ent_sqm to 2 decimal places
        map_df["rent_sqm"] = map_df["rent_sqm"].round(2)

        # Create heatmap data
        heatmap = self._create_heatmap_data(map_df)
        fig = go.Figure(data=[heatmap])

        if center_coords is None:
            # Calculate center coordinates as the mean of Latitude and Longitude columns in map_df
            center_coords = {
                "lat": map_df["Latitude"].mean(),
                "lon": map_df["Longitude"].mean(),
            }
        else:
            # Use the provided center_coords
            center_coords = {"lat": center_coords[0], "lon": center_coords[1]}

        # Add scattermapbox trace for the center marker
        fig.add_trace(
            go.Scattermapbox(
                lat=[center_coords["lat"]],
                lon=[center_coords["lon"]],
                mode="markers+text",
                marker=go.scattermapbox.Marker(size=10, color="red"),
                text=[center_marker_name],
                textposition="bottom right",
                showlegend=False,
            )
        )

        # Update figure with mapbox center, zoom, and height
        fig = self._update_fig(
            fig, mapbox_center=center_coords, mapbox_zoom=zoom, height=600
        )

        # Display title and map
        st.markdown(
            f"<h3 style='text-align: center;'>{title}</h3>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig, use_container_width=True)

    def _extract_lat_lon(self, coord):
        coord_parts = coord.strip("()").split(", ")
        coord_tuple = tuple(
            float(part) if part.strip() != "None" else None for part in coord_parts
        )
        return coord_tuple

    def _get_hovertemplate(self, row):
        labels = [
            "City:",
            "Complete Address:",
            "Total Price:",
            "Price:",
            "Rent:",
            "Square Meters:",
            "Price/Sqm:",
            "Furnished:",
        ]
        max_label_length = max(len(label) for label in labels)
        font_style = "font-family:monospace;"

        hover_tooltip = self.texts["hover_tooltip"]
        city = hover_tooltip["city"]
        street = hover_tooltip["street"]
        total_price = hover_tooltip["price_total"]
        price = hover_tooltip["price"]
        rent = hover_tooltip["rent"]
        sqm = hover_tooltip["area"]
        rent_sqm = hover_tooltip["price_per_meter"]
        furnished = hover_tooltip["furnished"]
        boolean_values = hover_tooltip["boolean"]
        nan = hover_tooltip["nan"]

        def format_nan_value(value):
            if pd.isna(value) or value == "":
                return nan
            else:
                return value

        def _format_street_address(row, max_label_length):
            street_label = f"{street}:"
            street_address = (
                row["complete_address"].replace((", " + row["city"]), "")
                if row["city"]
                else row["complete_address"]
            )
            return f"<span style='{font_style}'>{street_label.ljust(max_label_length)}</span> {street_address}<br>"

        row = {col: format_nan_value(row[col]) for col in row.index}

        return (
            f"<span style='{font_style}'>{f'{city}:'.ljust(max_label_length)}</span> {row['city']}<br>"
            + _format_street_address(row, max_label_length)
            + f"<span style='{font_style}'>{f'{total_price}:'.ljust(max_label_length)}</span> {row['price_total']}<br>"
            f"<span style='{font_style}'>{f'{price}:'.ljust(max_label_length)}</span> {row['price']}<br>"
            f"<span style='{font_style}'>{f'{rent}:'.ljust(max_label_length)}</span> {row['rent']}<br>"
            f"<span style='{font_style}'>{f'{sqm}:'.ljust(max_label_length)}</span> {row['sqm']}<br>"
            f"<span style='{font_style}'>{f'{rent_sqm}:'.ljust(max_label_length)}</span> {row['rent_sqm']}<br>"
            f"<span style='{font_style}'>{f'{furnished}:'.ljust(max_label_length)}</span> {boolean_values[row['is_furnished']]}"
            "<extra></extra>"
        )

    def _create_heatmap_data(self, plot_data):
        plot_data["hovertemplate"] = plot_data.apply(self._get_hovertemplate, axis=1)
        offer_counts = (
            plot_data.groupby(["Latitude", "Longitude"])
            .size()
            .reset_index(name="offer_count")
        )
        plot_data = plot_data.merge(offer_counts, on=["Latitude", "Longitude"])

        return go.Densitymapbox(
            lat=plot_data["Latitude"],
            lon=plot_data["Longitude"],
            z=plot_data["offer_count"],
            radius=10,
            colorscale="Viridis",
            zmin=0,
            zmax=plot_data["offer_count"].max(),
            hovertemplate=plot_data["hovertemplate"],
            colorbar={"title": self.legend_title},
        )

    def _update_fig(self, fig, mapbox_zoom, mapbox_center, height=None):
        layout_update = {
            "mapbox_style": "carto-positron",
            "mapbox_zoom": mapbox_zoom,
            "mapbox_center": mapbox_center,
            "margin": {"l": 0, "r": 0, "t": 40, "b": 0},
            "coloraxis_colorbar": {
                "title": self.legend_title,
                "title_side": "right",
                "title_font": {"size": 20},
                "y": -2,
                "yanchor": "middle",
            },
        }

        if height is not None:
            layout_update["height"] = height

        fig.update_layout(**layout_update)
        return fig
