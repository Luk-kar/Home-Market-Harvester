"""
This module provides utility functions to assist 
in the scraping of real estate offers from web pages. 
It includes functions to check 
the existence of offers, extract offer URLs, normalize these URLs, 
and determine the presence of pagination on a web page.
The module leverages the Selenium WebDriver 
for webpage interaction and navigation.
"""

# Standard imports
import logging

# Third-party imports
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

# Local imports
from pipeline.config.a_scraping import LOGGING


def has_offer(driver: WebDriver, selector: str) -> bool:
    """
    Check if there is an offer on the page.

    Args:
        driver (WebDriver): The WebDriver instance for interacting with the browser.
        selector (str): The CSS selector for identifying the offer.

    Returns:
        bool: True if an offer is found, False otherwise.
    """
    try:
        driver.find_element(By.CSS_SELECTOR, selector)
        return True
    except NoSuchElementException:
        return False


def extract_offer_urls(offers: list) -> list:
    """
    Extract the URLs of the offers.

    Args:
        offers (list): List of offer elements.

    Returns:
        list: List of offer URLs.
    """
    url_offers = []
    for offer in offers:
        first_anchor_tag = offer.select_one("a")
        if first_anchor_tag:
            href_link = first_anchor_tag["href"]
            url_offers.append(href_link)
        else:
            if LOGGING["debug"]:
                offer_id = offer["id"] if "id" in offer.attrs else "Unknown"
                logging.info("No link found in the offer with id=%s", offer_id)
    return url_offers


def normalize_offer_url(offer_url: str, olx_domain: str) -> str:
    """
    Normalize the offer URL by adding the domain if it's missing.

    Args:
        offer_url (str): The offer URL.
        olx_domain (str): The OLX domain.

    Returns:
        str: The normalized offer URL.
    """
    if not offer_url.startswith("http"):
        offer_url = olx_domain + offer_url
    return offer_url


def has_next_page(driver: WebDriver, selector: str) -> bool:
    """
    Check if there is a next page button.

    Args:
        driver (WebDriver): The WebDriver instance for interacting with the browser.
        selector (str): The CSS selector for identifying the next page button.

    Returns:
        bool: True if a next page button is found, False otherwise.
    """
    try:
        next_page_button = driver.find_element(By.CSS_SELECTOR, selector)
        return True
    except NoSuchElementException:
        return False
