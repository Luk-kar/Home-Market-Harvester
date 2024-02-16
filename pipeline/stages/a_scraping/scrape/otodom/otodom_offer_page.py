"""
This module contains functions for managing 
and processing real estate offers from the Otodom website 
in a web scraping context. 
It includes functionality to open individual offer pages in new browser windows, 
extract relevant data using the Selenium WebDriver, 
save the extracted data to CSV files, 
and handle any exceptions that occur during the process. 
The module integrates counter tracking to monitor scraping progress 
and manages the switching between browser windows 
to ensure seamless data collection from multiple offers.
"""

# Standard imports
import logging

# Third-party imports
from enlighten import Counter
from selenium.webdriver.remote.webdriver import WebDriver

# Local imports
from pipeline.stages.a_scraping._utils.selenium_utils import humans_delay
from pipeline.stages.a_scraping.config import DOMAINS, SCRAPER, LOGGING
from pipeline.stages.a_scraping.csv_manager import save_to_csv
from pipeline.stages.a_scraping.scrape.custom_errors import OfferProcessingError
from pipeline.stages.a_scraping.scrape.otodom.extract_offer_otodom import (
    scrape_offer_page,
)


def open_process_and_close_window(
    driver: WebDriver,
    original_window: str,
    offer_url: str,
    location_query: str,
    timestamp: str,
    progress: Counter,
    scraped_urls: set[str],
):
    """
    Opens the offer in a new window, processes the offer data, saves it to a CSV file,
    and closes the window.

    Args:
        driver (WebDriver): The WebDriver instance used for web scraping.
        original_window (str): The original previous window handle.
        offer_url (str): The URL of the offer to process.
        location_query (str): The location query used for scraping.
        timestamp (str): The timestamp of the scraping process.
        progress (Counter): The progress counter used to track the number of processed offers.
        scraped_urls (set[str]): The set of scraped URLs.

    Returns:
        None
    """
    open_offer(driver, offer_url)

    if SCRAPER["anti_anti_bot"]:
        humans_delay()

    record = scrape_offer_page(driver)

    if record:
        save_to_csv(record, location_query, DOMAINS["otodom"], timestamp)
        progress.update()
        scraped_urls.add(offer_url)
    else:
        logging.error("Failed to process: %s", offer_url)
        if LOGGING["debug"]:
            raise OfferProcessingError(offer_url, "Failed to process offer URL")

    driver.close()

    driver.switch_to.window(original_window)


def open_offer(driver: WebDriver, offer_url: str):
    """
    Opens the offer page in a new window/tab using the provided WebDriver instance.

    Args:
        driver (WebDriver): The WebDriver instance used to control the browser.
        offer_url (str): The URL of the offer to open.

    Returns:
        None
    """
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    full_link = DOMAINS["otodom"] + offer_url
    driver.get(full_link)
