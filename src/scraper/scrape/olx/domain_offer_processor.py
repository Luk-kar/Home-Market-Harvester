# Standard imports
import logging

# Third-party imports
from enlighten import Counter
from selenium.webdriver.remote.webdriver import WebDriver


# Local imports
from csv_manager import save_to_csv
from config import LOGGING
from scrape.olx.extract_offer_olx import scrape_offer as process_offer_olx
from scrape.otodom.extract_offer_otodom import extract_data as process_offer_otodom
from scrape.custom_errors import OfferProcessingError


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
        None
    """
    record = process_offer_olx(driver)
    if record:
        save_to_csv(record, location_query, domain, timestamp)
        progress.update()
    else:
        offer_url = driver.current_url
        logging.error("Failed to process: %s", offer_url)
        if LOGGING["debug"]:
            raise OfferProcessingError(offer_url, "Failed to process offer URL")


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
        None
    """
    record = process_offer_otodom(driver)
    if record:
        save_to_csv(record, location_query, domain, timestamp)
        progress.update()
    else:
        offer_url = driver.current_url
        logging.error("Failed to process: %s", offer_url)
        if LOGGING["debug"]:
            raise OfferProcessingError(offer_url, "Failed to process offer URL")
