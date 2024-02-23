"""
This module integrates various utilities for data manipulation, 
geocoding, and travel time calculation, primarily designed for 
enhancing real estate market data with geographical insights and connectivity metrics.

Key Functionalities:
- Project root setup for consistent file referencing across the project.
- Configuration management for accessing and managing project settings.
- Data preprocessing including filtering and cleaning of real estate data.
- Geocoding capabilities to convert addresses into geographic coordinates using the Nominatim API.
- Integration with third-party APIs such as OpenRouteService 
  to calculate travel times between locations.

Usage:
This module is designed to be used as part of 
a larger pipeline in real estate data analysis projects. 
It requires external configuration and environmental variables to be set up, 
including API keys for geolocation and travel time services.

Note:
Ensure that all required environmental variables 
and configurations are properly set before using this module. 
This includes API keys and project-specific settings like 
the destination coordinates for travel time calculations.
"""

# Standard imports
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional
import math
import os
import pandas as pd
import sys
import time
import warnings

# Suppress future warnings
warnings.simplefilter(action="ignore", category=FutureWarning)

# Third-party imports
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.geocoders import Nominatim
import enlighten
import numpy as np
import requests


# Set the project root
def set_project_root() -> Path:
    """
    Sets the project root and appends it to the system path.

    Returns:
        Path: The root directory of the project.
    """
    project_root = Path(__file__).resolve().parents[3]
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))
    return project_root


project_root = set_project_root()

# Local imports
from pipeline.config._conf_file_manager import ConfigManager
from pipeline.stages._csv_utils import DataPathCleaningManager
from pipeline.components.logging import log_and_print, setup_logging

setup_logging()


def get_recent_data_timeplace() -> str:
    """
    Get the most recent data timeplace from the configuration file.

    Returns:
        str: The most recent data timeplace.

    Raises:
        ValueError: If the configuration variable is not set.
    """

    config_file = ConfigManager(
        str(project_root / "pipeline" / "config" / "run_pipeline.conf")
    )
    TIMEPLACE = "MARKET_OFFERS_TIMEPLACE"
    data_timeplace = config_file.read_value(TIMEPLACE)

    if data_timeplace is None:
        message = f"The configuration variable {TIMEPLACE} is not set."
        log_and_print(message, level="error")
        raise ValueError(message)
    return data_timeplace


def get_destination_coords() -> tuple[float, float]:
    """
    Get the destination coordinates from the environment variables.

    Returns:
        tuple: The destination coordinates.
    """

    destination_coords = os.getenv("DESTINATION_COORDINATES")
    if not destination_coords:
        message = "DESTINATION_COORDINATES is not set."
        log_and_print(message, level="error")
        raise ValueError(message)

    try:
        destination_coords_sanitized = tuple(map(float, destination_coords.split(",")))
    except ValueError as exc:
        message = (
            "DESTINATION_COORDINATES is not in the correct format."
            f"Value\n:{destination_coords}\n"
            f"{exc}"
        )
        log_and_print(message, level="error")
        raise ValueError(message) from exc

    return destination_coords_sanitized


def filter_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter the columns of the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to filter.

    Returns:
        pd.DataFrame: The filtered DataFrame.
    """

    df_temp = pd.DataFrame()
    df_temp["complete_address"] = df[("location", "complete_address")]
    df_temp["city"] = df[("location", "city")] + ", " + df[("location", "voivodeship")]
    df_temp["price_total"] = df[("pricing", "total_rent")]
    df_temp["price"] = df[("pricing", "price")]
    df_temp["rent"] = df[("pricing", "rent")]
    df_temp["rent_sqm"] = df[("pricing", "total_rent_sqm")]
    df_temp["sqm"] = df[("size", "square_meters")]
    df_temp["is_furnished"] = df[("equipment", "furniture")]

    return df_temp


def get_geolocator(user_agent: str) -> Nominatim:
    """
    Creates a geolocator object with the specified user agent.

    Args:
        user_agent (str): The user agent to be used for geolocation requests.

    Returns:
        Nominatim: Geolocator instance.
    """
    return Nominatim(user_agent=user_agent)


def get_coordinates(
    geolocator: Nominatim, address: str, attempt: int = 1, max_attempts: int = 3
) -> tuple[Optional[float], Optional[float]]:
    """
    Attempts to get the coordinates of the given address.

    Args:
        geolocator (Nominatim): The geolocator object.
        address (str): The address to get coordinates for.
        attempt (int): Current attempt number.
        max_attempts (int): Maximum number of attempts.

    Returns:
        Tuple[Optional[float], Optional[float]]: The latitude and longitude of the address,
                                                or (None, None) if not found.
    """
    try:
        location = geolocator.geocode(address, timeout=10)
        return (location.latitude, location.longitude) if location else (None, None)
    except (GeocoderTimedOut, GeocoderUnavailable):
        if attempt <= max_attempts:
            time.sleep(1 * attempt)
            return get_coordinates(geolocator, address, attempt + 1, max_attempts)
        return (None, None)


def add_geo_data_to_offers(
    df_input: pd.DataFrame, geolocator: Nominatim
) -> pd.DataFrame:
    """
    Adds geographical data to the offers DataFrame.

    Args:
        df (pd.DataFrame): The offers DataFrame.
        geolocator (Nominatim): The geolocator object.

    Returns:
        pd.DataFrame: The offers DataFrame with geographical data.
    """
    df_temp = pd.DataFrame()
    df_temp["complete_address"] = df_input[("location", "complete_address")]
    df_temp["city"] = (
        df_input[("location", "city")] + ", " + df_input[("location", "voivodeship")]
    )

    # Create unique address list
    unique_addresses = df_temp["complete_address"].drop_duplicates()
    address_coords = {}

    manager = enlighten.get_manager()
    address_bar = manager.counter(
        total=len(unique_addresses), desc="Geocoding Addresses", unit="addresses"
    )

    def fetch_coords(address):
        coords = get_coordinates(geolocator, address)
        if coords == (None, None):
            # Fallback to city if complete address fails
            city = df_temp.loc[df_temp["complete_address"] == address, "city"].iloc[0]
            coords = get_coordinates(geolocator, city)
        return address, coords

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(fetch_coords, address): address
            for address in unique_addresses
        }
        for future in as_completed(futures):
            address, coords = future.result()
            address_coords[address] = coords
            address_bar.update()

    manager.stop()

    # Map the coordinates back to the DataFrame
    coords = df_temp["complete_address"].map(address_coords)

    return coords


def calculate_time_travels(
    start_coords: pd.Series, destination_coords: tuple[float, float]
) -> pd.Series:
    """
    Calculate the travel times for each address in the DataFrame to a given destination.

    Args:
        start_coords (pd.Series): A Pandas Series of start coordinates (latitude, longitude tuples).
        destination_coords (tuple[float, float]): A tuple representing
                                                  the destination coordinates (latitude, longitude).

    Returns:
        pd.Series: A Pandas Series of travel times to the destination from each start coordinate.
    """

    api_key = os.getenv("OPENROUTESERVICE_API_KEY")
    if not api_key:
        message = "OPENROUTESERVICE_API_KEY is not provided or invalid."
        log_and_print(message, level="error")
        raise ValueError(message)

    if not isinstance(destination_coords, tuple) or len(destination_coords) != 2:
        message = (
            "Destination coordinates must be a tuple of two floats.\n"
            f"destination_coords:\n{destination_coords}"
        )
        log_and_print(message, level="error")
        raise ValueError(message)

    unique_coords = start_coords.drop_duplicates()
    travel_times_for_unique_coords = {}

    manager = enlighten.get_manager()
    travel_time_bar = manager.counter(
        total=len(unique_coords),
        desc="Calculating Travel Times",
        unit="addresses",
    )

    for start_coord in unique_coords:
        try:
            # Assuming get_travel_time function exists and calculates the travel time
            travel_time = get_travel_time(start_coord, destination_coords, api_key)
            travel_times_for_unique_coords[start_coord] = travel_time
            travel_time_bar.update()
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.RequestException,
            KeyError,
        ) as api_call_exception:
            print(f"An error occurred: {api_call_exception}")
            continue
        except Exception as exc:
            message = f"An unexpected error occurred: {exc}"
            log_and_print(message, level="error")
            raise exc

    manager.stop()

    # Map the calculated travel times back to all start coordinates
    all_travel_times = start_coords.map(travel_times_for_unique_coords)

    return all_travel_times


def get_travel_time(
    coords_start: tuple[float, float], coords_end: tuple[float, float], api_key: str
) -> float:
    """
    Calculate the travel time between two points using OpenRouteService.
    """
    start_lat, start_lon = coords_start
    end_lat, end_lon = coords_end

    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {"Authorization": api_key}
    params = {"start": f"{start_lon},{start_lat}", "end": f"{end_lon},{end_lat}"}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()  # Raises HTTPError for bad responses
        data = response.json()

        if "features" in data and data["features"]:
            try:
                travel_time_seconds = data["features"][0]["properties"]["segments"][0][
                    "duration"
                ]

                if travel_time_seconds is None or travel_time_seconds < 0:

                    message = (
                        "Invalid travel time data found in response.\n"
                        "travel_time_seconds:\n"
                        f"{travel_time_seconds}"
                    )
                    log_and_print(message, level="warning")

                    return np.nan

                travel_time_minutes = math.ceil(travel_time_seconds / 60)
                print(f"Travel time: {travel_time_minutes} minutes")
                return travel_time_minutes

            except KeyError as key_err:

                print(f"Expected duration data is missing in the response.\n{key_err}")
                return np.nan
        else:

            print(
                "No route or travel time data found in response."
                "No 'features' key in response data."
            )
            return np.nan

    except requests.exceptions.HTTPError as http_err:
        message = f"HTTP error occurred: {http_err}"
        log_and_print(message, level="warning")

    except requests.exceptions.ConnectionError as conn_err:
        message = f"Connection error occurred: {conn_err}"
        log_and_print(message, level="warning")

    except requests.exceptions.Timeout as timeout_err:
        message = f"Timeout error occurred: {timeout_err}"
        log_and_print(message, level="warning")

    except requests.exceptions.RequestException as req_err:
        message = f"Unexpected error occurred: {req_err}"
        log_and_print(message, level="warning")

    except KeyError as key_err:
        message = f"Key error in parsing response data: {key_err}"
        log_and_print(message, level="warning")

    return np.nan


def main():
    """
    Main function for creating the map data.
    """
    data_timeplace = get_recent_data_timeplace()

    data_path_manager = DataPathCleaningManager(data_timeplace, project_root)
    combined_df = data_path_manager.load_df(domain="combined", is_cleaned=True)

    map_df = filter_columns(combined_df)

    log_and_print("Adding geographical data to the offers DataFrame.")
    geolocator = get_geolocator(user_agent="your_app_name")
    coords = add_geo_data_to_offers(combined_df, geolocator)
    log_and_print("Geographical data added.")

    log_and_print("Calculating travel times to the destination.")
    destination_coords = get_destination_coords()
    map_df["coords"] = coords
    map_df["travel_time"] = calculate_time_travels(coords, destination_coords)
    log_and_print("Travel times calculated.")

    data_path_manager.save_df(map_df, "map")


if __name__ == "__main__":
    main()
