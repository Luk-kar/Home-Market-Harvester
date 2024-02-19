"""
module is designed to configure and manage data and model paths for a data processing application. 
It utilizes environment variables to dynamically set paths for user data, market data, and model files, 
providing flexibility and customizability for different runtime environments.
"""

# Standard imports
from os import getenv
from pathlib import Path

# Local imports
from pipeline.config._conf_file_manager import ConfigManager


def load_timeplace():
    """
    Load the time and place of the market data from the configuration file.
    """

    config_file = ConfigManager("run_pipeline.conf")
    TIMEPLACE = "MARKET_OFFERS_TIMEPLACE"
    data_timeplace = config_file.read_value(TIMEPLACE)

    if not data_timeplace:
        raise ValueError(f"The configuration variable {TIMEPLACE} is not set.")

    return data_timeplace


def _warn_default_usage(env_var_name):
    print(
        f"WARNING: You are using the default {env_var_name.split('_')[0].lower()}. "
        f"Set the {env_var_name} environment variable to use your own."
    )


# Constants
data_timeplace = load_timeplace()

if not data_timeplace:
    raise ValueError("The configuration variable MARKET_OFFERS_TIMEPLACE is not set.")

_USER_DATA_PATH_DEFAULT = str(Path("data", "test", "your_offers.csv"))

DATA = {
    "user_data_path": getenv("USER_OFFERS_PATH", _USER_DATA_PATH_DEFAULT),
    "market_data_datetime": data_timeplace,
}

MODEL = {
    "model_path": str(Path("model", data_timeplace, "model.pkl")),
}

# Warning messages
if DATA["user_data_path"] == _USER_DATA_PATH_DEFAULT:
    _warn_default_usage("USER_OFFERS_PATH")
