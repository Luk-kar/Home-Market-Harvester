"""
module is designed to configure and manage data and model paths for a data processing application. 
It utilizes environment variables to dynamically set paths for user data, market data, and model files, 
providing flexibility and customizability for different runtime environments.
"""

# Standard imports
from os import getenv
from pathlib import Path

# Local imports
from pipeline.config._config_manager import ConfigManager


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


data_timeplace = load_timeplace()


def _warn_default_usage(env_var_name):
    print(
        f"WARNING: You are using the default {env_var_name.split('_')[0].lower()}. "
        f"Set the {env_var_name} environment variable to use your own."
    )


# Constants
_USER_DATA_PATH_DEFAULT = str(Path("data", "test", "your_offers.csv"))
_MODEL_PATH_DEFAULT = str(
    Path("pipeline", "src", "c_model_developing", "model", "model.pkl")
)

DATA = {
    "user_data_path": getenv("USER_OFFERS_PATH", _USER_DATA_PATH_DEFAULT),
    "market_data_datetime": data_timeplace,
}

MODEL = {
    "model_path": getenv("MODEL_PATH", _MODEL_PATH_DEFAULT),
}

# Warning messages
if DATA["user_data_path"] == _USER_DATA_PATH_DEFAULT:
    _warn_default_usage("USER_OFFERS_PATH")

if MODEL["model_path"] == _MODEL_PATH_DEFAULT:
    _warn_default_usage("MODEL_PATH")
