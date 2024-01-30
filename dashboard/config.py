# Standard imports
import os

DATA = {
    "user_data_path": os.getenv("YOUR_OFFERS_PATH", "data\\test\\your_offers.csv"),
    "market_data_path": "data/offers.csv",
}

MODEL = {
    "model_path": "model/model.pkl",
    "model_metadata_path": "model/model_columns.pkl",
}
