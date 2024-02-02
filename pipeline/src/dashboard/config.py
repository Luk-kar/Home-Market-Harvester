"""
module is designed to configure and manage data and model paths for a data processing application. 
It utilizes environment variables to dynamically set paths for user data, market data, and model files, 
providing flexibility and customizability for different runtime environments.
"""
# Standard imports
from os import getenv
from pathlib import Path

# Local imports
from pipeline.src._csv_utils import (
    data_timeplace,
)


def _warn_default_usage(env_var_name):
    print(
        f"WARNING: You are using the default {env_var_name.split('_')[0].lower()}. "
        f"Set the {env_var_name} environment variable to use your own."
    )


# Constants
_USER_DATA_PATH_DEFAULT = str(Path("data", "test", "your_offers.csv"))
_MODEL_PATH_DEFAULT = str(Path("pipeline", "src", "dashboard", "model", "model.pkl"))

DATA = {
    "user_data_path": getenv("USER_OFFERS_PATH", _USER_DATA_PATH_DEFAULT),
    "market_data_datetime": getenv("MARKET_OFFERS_TIMEPLACE", data_timeplace),
}

MODEL = {
    "model_path": getenv("MODEL_PATH", _MODEL_PATH_DEFAULT),
}

# Warning messages
if DATA["user_data_path"] == _USER_DATA_PATH_DEFAULT:
    _warn_default_usage("USER_OFFERS_PATH")

if DATA["market_data_datetime"] == data_timeplace:
    _warn_default_usage("MARKET_OFFERS_TIMEPLACE")

if MODEL["model_path"] == _MODEL_PATH_DEFAULT:
    _warn_default_usage("MODEL_PATH")
