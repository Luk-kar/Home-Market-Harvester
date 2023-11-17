import logging
from typing import Dict, Any

SCRAPER: Dict[str, str | int | float] = {
    "location": "Katowice",
    "domain": "https://www.olx.pl",
    "category": "nieruchomosci/mieszkania/wynajem/",
    "max_retries": 5,
    "multi_wait_timeout": 5,
    "wait_timeout": 10,
    "min_delay": 0.90,
    "max_delay": 1.30,
}
WEBDRIVER: Dict[str, str | bool] = {
    "user_agent": "random",  # Use 'random' for random user agent or specify a string
    "headless": True,
    "maximize_window": True,
}
LOGGING: Dict[str, str] = {
    "level": logging.INFO,
    "file": "./logs/scraper.log",
}
SUBDOMAINS: Dict[str, str] = {
    "olx": "https://www.olx.pl",
    "otodom": "https://www.otodom.pl",
}
