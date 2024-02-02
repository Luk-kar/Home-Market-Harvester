"""
This module provides functionality for processing real estate offers 
from OLX and Otodom websites. 
It includes functions to handle individual offer processing for each site, 
utilizing Selenium WebDriver for web interactions. 
The module is responsible for extracting offer data, saving it in CSV format, 
and managing the progress of the scraping task. 
It employs robust error handling and logging mechanisms 
to deal with and report any issues 
encountered during the offer processing stage.
"""

# Standard imports
import logging

# Third-party imports
from enlighten import Counter
from selenium.webdriver.remote.webdriver import WebDriver


# Local imports
from pipeline.src.scraper.csv_manager import save_to_csv
from pipeline.src.scraper.config import LOGGING
from pipeline.src.scraper.scrape.olx.extract_offer_olx import (
    scrape_offer as process_offer_olx,
)
from pipeline.src.scraper.scrape.otodom.extract_offer_otodom import (
    scrape_offer_page as process_offer_otodom,
)
from pipeline.src.scraper.scrape.custom_errors import OfferProcessingError


def process_olx_offer(
    driver: WebDriver,
    location_query: str,
    domain: str,
    timestamp: str,
    progress: Counter,
):
    """
    Process an OLX offer.

    Args:
        driver (WebDriver): The WebDriver instance for interacting with the browser.
        location_query (str): The location query for the offer.
        domain (str): The domain of the offer.
        timestamp (str): The timestamp for the current scraping process.
        progress (Counter): The counter for tracking the progress of scraping.

    Returns:
        str: The URL of the processed offer if successful, None otherwise.
    """
    record = process_offer_olx(driver)
    offer_url = driver.current_url

    if record:
        save_to_csv(record, location_query, domain, timestamp)
        progress.update()
        return offer_url

    else:
        logging.error("Failed to process: %s", offer_url)
        if LOGGING["debug"]:
            raise OfferProcessingError(offer_url, "Failed to process offer URL")
        return None


def process_otodom_offer(
    driver: WebDriver,
    location_query: str,
    domain: str,
    timestamp: str,
    progress: Counter,
):
    """
    Process an OtoDom offer.

    Args:
        driver (WebDriver): The WebDriver instance for interacting with the browser.
        location_query (str): The location query for the offer.
        domain (str): The domain of the offer.
        timestamp (str): The timestamp for the current scraping process.
        progress (Counter): The counter for tracking the progress of scraping.

    Returns:
        str: The URL of the processed offer if successful, None otherwise.
    """
    record = process_offer_otodom(driver)
    offer_url = driver.current_url

    if record:
        save_to_csv(record, location_query, domain, timestamp)
        progress.update()
        return offer_url
    else:
        offer_url = driver.current_url
        logging.error("Failed to process: %s", offer_url)
        if LOGGING["debug"]:
            raise OfferProcessingError(offer_url, "Failed to process offer URL")
        return None
