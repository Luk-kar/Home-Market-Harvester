# Standard imports
from pathlib import Path
import sys
import time
import warnings
import pandas as pd

# Suppress future warnings
warnings.simplefilter(action="ignore", category=FutureWarning)

# Third-party imports
import enlighten
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.geocoders import Nominatim


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
from pipeline.config._config_manager import ConfigManager
from pipeline.src._csv_utils import DataPathCleaningManager


def get_geolocator(user_agent: str) -> Nominatim:
    """
    Creates a geolocator object with the specified user agent.

    Args:
        user_agent (str): The user agent to be used for geolocation requests.

    Returns:
        Nominatim: Geolocator instance.
    """
    return Nominatim(user_agent=user_agent)


def get_coordinates(geolocator, address, attempt=1, max_attempts=3) -> tuple:
    """
    Attempts to get the coordinates of the given address.

    Args:
        geolocator: The geolocator object.
        address (str): The address to get coordinates for.
        attempt (int): Current attempt number.
        max_attempts (int): Maximum number of attempts.

    Returns:
        tuple: The latitude and longitude of the address.
    """
    try:
        location = geolocator.geocode(address, timeout=10)
        return (location.latitude, location.longitude) if location else (None, None)
    except (GeocoderTimedOut, GeocoderUnavailable):
        if attempt <= max_attempts:
            time.sleep(1 * attempt)
            return get_coordinates(geolocator, address, attempt + 1, max_attempts)
        return (None, None)


def add_geo_data_to_offers(df: pd.DataFrame, geolocator) -> pd.DataFrame:
    """
    Adds geographical data to the offers DataFrame.

    Args:
        df (pd.DataFrame): The offers DataFrame.
        geolocator: The geolocator object.

    Returns:
        pd.DataFrame: The offers DataFrame with geographical data.
    """
    df_temp = pd.DataFrame()
    df_temp["complete_address"] = df[("location", "complete_address")]
    df_temp["city"] = df[("location", "city")] + ", " + df[("location", "voivodeship")]

    # Create unique address list
    unique_addresses = df_temp["complete_address"].unique()
    address_coords = {}

    manager = enlighten.get_manager()
    address_bar = manager.counter(
        total=len(unique_addresses), desc="Processing", unit="addresses"
    )

    for address in unique_addresses:
        coords = get_coordinates(geolocator, address)
        if coords == (None, None):
            # If coordinates for the complete address are not found, try with city
            city = df_temp[df_temp["complete_address"] == address]["city"].values[0]
            coords = get_coordinates(geolocator, city)
        address_coords[address] = coords
        address_bar.update()

    manager.stop()

    # Map the coordinates back to the DataFrame
    coords = df_temp["complete_address"].map(address_coords)

    return coords


def get_recent_data_timeplace():
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
        raise ValueError(f"The configuration variable {TIMEPLACE} is not set.")
    return data_timeplace


def filter_columns(df: pd.DataFrame):
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


def main():
    data_timeplace = get_recent_data_timeplace()

    data_path_manager = DataPathCleaningManager(data_timeplace, project_root)
    combined_df = data_path_manager.load_df(domain="combined", is_cleaned=True)

    map_df = filter_columns(combined_df)

    geolocator = get_geolocator(user_agent="your_app_name")
    map_df["coords"] = add_geo_data_to_offers(combined_df, geolocator)

    data_path_manager.save_df(map_df, "map")


if __name__ == "__main__":
    main()
