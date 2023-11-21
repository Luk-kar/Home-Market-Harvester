"""
This module contains configuration settings for a web scraping application. 

It defines configurations for scraper behavior including:
location, 
domain, 
category, 
and various timeouts and delays to mimic human interaction and avoid bot detection. 

It also sets up WebDriver preferences including path, user agent, and display options. 
Additionally, the module configures logging parameters and 
specifies subdomains for targeted websites. 

These configurations are essential for controlling and 
customizing the scraper's performance and interactions with web elements.
"""

# Standard imports
import logging

SCRAPER: dict[str, str | int | float] = {
    "location": "Katowice",
    "domain": "https://www.olx.pl",
    "category": "nieruchomosci/mieszkania/wynajem/",
    "max_retries": 5,
    "multi_wait_timeout": 5,
    "wait_timeout": 10,
    "min_delay": 0.90,
    "max_delay": 1.30,
    "anti-anti-bot": True,  # Make the scraper more human-like and also slower
}
WEBDRIVER: dict[str, str | bool] = {
    "auto_install": False,
    "path": "src\\scraper\\chromedriver.exe",  # Path to the webdriver
    "user_agent": "random",  # Use 'random' for random user agent or specify a string
    "headless": False,
    "maximize_window": True,
}
LOGGING: dict[str, str] = {
    "debug": True,
    "level": logging.INFO,
    "file": "./logs/scraper.log",
}
SUBDOMAINS: dict[str, str] = {
    "olx": "https://www.olx.pl",
    "otodom": "https://www.otodom.pl",
}
