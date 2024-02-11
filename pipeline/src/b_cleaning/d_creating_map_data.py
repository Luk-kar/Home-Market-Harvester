# Standard imports
from pathlib import Path
import sys
import time
import warnings
import pandas as pd

# Suppress future warnings
warnings.simplefilter(action="ignore", category=FutureWarning)

# Third-party imports
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.geocoders import Nominatim


# Set the project root
def set_project_root() -> Path:
    """
    Sets the project root and appends it to the system path.

    Returns:
        Path: The root directory of the project.
    """
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        print(f"The root directory of the project is: {project_root}")
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
    df_temp = df.copy()
    df_temp["coords"] = df_temp[("location", "complete_address")].apply(
        lambda addr: get_coordinates(geolocator, addr)
    )
    return df_temp


def get_recent_data_timeplace():
    """
    Get the most recent data timeplace from the configuration file.

    Returns:
        str: The most recent data timeplace.

    Raises:
        ValueError: If the configuration variable is not set.
    """

    config_file = ConfigManager(project_root / "run_pipeline.conf")
    TIMEPLACE = "MARKET_OFFERS_TIMEPLACE"
    data_timeplace = config_file.read_value(TIMEPLACE)

    if data_timeplace is None:
        raise ValueError(f"The configuration variable {TIMEPLACE} is not set.")
    return data_timeplace


def main():
    data_timeplace = get_recent_data_timeplace()

    data_path_manager = DataPathCleaningManager(data_timeplace, project_root)
    combined_df = data_path_manager.load_df(domain="combined", is_cleaned=True)

    geolocator = get_geolocator(user_agent="your_app_name")
    map_df = add_geo_data_to_offers(combined_df, geolocator)

    data_path_manager.save_df(map_df, "map")


if __name__ == "__main__":
    main()
