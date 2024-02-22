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
from pathlib import Path
import logging
import os

# Local imports
from pipeline.stages.a_scraping._utils.string_transformations import sanitize_path

SCRAPER: dict[str, str | int | float] = {
    # Any you choose, but remember to use the same format as on the website
    "location_query": "Mierzęcice, Będziński, Śląskie",  # Default when no arguments are passed
    "area_radius": 25,  # 0km, 5km, 10km, 15km, 25km, 50km, 75km # Default when no arguments are passed
    "max_retries": 5,
    "wait_timeout": 10,
    "multi_wait_timeout": 5,
    "min_delay": 0.90,
    "max_delay": 1.30,
    "anti_anti_bot": True,  # Make the scraper more human-like and but also slower
    "scraped_offers_cap": 3,  # Default when no arguments are passed
}
WEBDRIVER: dict[str, str | bool] = {
    "auto_install": False,
    "path": sanitize_path(
        os.getenv(
            "CHROME_DRIVER_PATH",
            Path("pipeline") / "stages" / "a_scraping"
            "chrome" / "119.0.6045.105" / "chromedriver.exe",
        )
    ),
    "user_agent": "random",  # Use 'random' for random user agent or specify a string
    "headless": True,  # Set to False to see the browser, watch out LOGGING["debug"]
    "ignore_certificate_errors": True,  # Errors could break the scraper
    "maximize_window": True,
}
WEBBROWSER: dict[str, str] = {
    "binary_location_path": sanitize_path(
        os.getenv(
            "CHROME_BROWSER_PATH",
            Path("pipeline")
            / "stages"
            / "a_scraping"
            / "chrome"
            / "119.0.6045.105"
            / "chrome.exe",
        )
    ),
}
LOGGING: dict[str, str] = {
    "debug": False,  # also sets the headless option to True
    "level": logging.INFO,
    "file": sanitize_path("./logs/a_scraping.log"),
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


class ConfigurationError(Exception):
    """Exception raised for errors in the configuration settings."""


def check_path_exists(path: str, config_name: str):
    """
    Checks if the given path exists. Raises an exception if the path does not exist.

    Parameters:
        path (str): The path to check.
        config_name (str): The name of the configuration setting being checked.

    Raises:
        ConfigurationError: If the path does not exist.
    """
    if not os.path.exists(path):
        raise ConfigurationError(
            (f"\nThe path:\n{path}\n" f"specified for:\n{config_name}")
        )


check_path_exists(WEBDRIVER["path"], "WEBDRIVER['path']")
check_path_exists(
    WEBBROWSER["binary_location_path"], "WEBBROWSER['binary_location_path']"
)
check_path_exists(DATA["folder_scraped_data"], "DATA['folder_scraped_data']")
