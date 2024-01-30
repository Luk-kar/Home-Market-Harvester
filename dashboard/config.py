# Standard imports
import os

# Local imports
from notebooks._csv_utils import (
    data_timeplace,
)  # pylint: disable=wrong-import-position

DATA = {
    "user_data_path": os.getenv("YOUR_OFFERS_PATH", "data\\test\\your_offers.csv"),
    "market_data_datetime": data_timeplace,  # like: "2023_11_27_19_41_45_Mierzęcice__Będziński__Śląskie"
}

MODEL = {
    "model_path": "model/model.pkl",
    "model_metadata_path": "model/model_columns.pkl",
}
