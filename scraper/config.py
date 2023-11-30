"""
This module contains configuration settings for a web scraping application. 

It defines configurations for scraper behavior including:
location, 
domain, 
category, 
and various timeouts and delays to mimic human interaction and avoid bot detection. 

It also sets up WebDriver preferences including path, user agent, and display options. 
Additionally, the module configures logging parameters and 
specifies targeted websites. 

These configurations are essential for controlling and 
customizing the scraper's performance and interactions with web elements.
"""

# Standard imports
import logging

# Local imports
from scraper._utils.string_transformations import sanitize_path


SCRAPER: dict[str, str | int | float] = {
    # Any you choose, but remember to use the same format as on the website
    "location_query": "Mierzęcice, Będziński, Śląskie",
    "area_radius": 25,  # 0km, 5km, 10km, 15km, 25km, 50km, 75km
    "max_retries": 5,
    "wait_timeout": 10,
    "multi_wait_timeout": 5,
    "min_delay": 0.90,
    "max_delay": 1.30,
    "anti_anti_bot": True,  # Make the scraper more human-like and also
    "scraped_offers_cap": 3,
}
WEBDRIVER: dict[str, str | bool] = {
    "auto_install": False,
    "path": sanitize_path("scraper\\chromedriver.exe"),  # Path to the webdriver
    "user_agent": "random",  # Use 'random' for random user agent or specify a string
    "headless": True,  # Set to False to see the browser, watch out LOGGING["debug"]
    "maximize_window": True,
}
LOGGING: dict[str, str] = {
    "debug": False,  # also sets the headless option to True
    "level": logging.INFO,
    "file": sanitize_path("./logs/scraper.log"),
}
DOMAINS: dict[str, str] = {
    "olx": {
        "domain": "https://www.olx.pl",
        "category": "nieruchomosci/mieszkania/wynajem/",
    },
    "otodom": "https://www.otodom.pl",
}
DATA: dict[str, str] = {
    "folder_scraped_data": sanitize_path("./data/raw/"),
    "encoding": "utf-8",
}
