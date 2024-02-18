"""
This module provides functions for scraping and extracting 
detailed information from real estate offer pages. 
It utilizes Selenium WebDriver for webpage navigation 
and BeautifulSoup for parsing HTML content. 
The main functionality includes processing individual offer pages 
to extract key details such as descriptions, prices, and listing specifics. 
Additionally, the module implements error handling and logging to manage 
exceptions that may occur during the scraping process.
"""

# Standard imports
from typing import Optional
import logging

# Third-party imports
from bs4 import BeautifulSoup
from selenium.webdriver.remote.webdriver import WebDriver

# Local imports
from pipeline.stages.a_scraping._utils.selenium_utils import (
    safe_get_text,
    wait_for_conditions,
    extract_data,
)
from pipeline.config.a_scraping import LOGGING
from pipeline.stages.a_scraping.scrape.custom_errors import OfferProcessingError


def scrape_offer(driver: WebDriver) -> Optional[dict[str, str]]:
    """
    Process the offer page and return the extracted information.

    Args:
        driver (WebDriver): The WebDriver instance used for scraping.

    Returns:
        Optional[dict[str, str]]: A dictionary containing the extracted information,
        or None if the offer page does not meet the required conditions.
    """
    field_selectors = {
        "description": '[data-testid="main"]',
        "location_paragraphs": 'img[src="/app/static/media/staticmap.65e20ad98.svg"]',
        "date": '[data-cy="ad-posted-at"]',
        "title": '[data-cy="ad_title"]',
        "price": '[data-testid="ad-price-container"]',
        "listing_details": "ul.css-sfcl1s > li",
        "summary_description": '[data-cy="ad_description"]',
    }

    conditions = [
        field_selectors[key] for key in ["description", "location_paragraphs"]
    ]

    if wait_for_conditions(driver, *conditions):
        return extract_offer_data(driver, field_selectors)
    else:
        offer_url = driver.current_url
        logging.error("Failed to process: %s", offer_url)
        if LOGGING["debug"]:
            raise OfferProcessingError(offer_url, "Failed to process offer URL")
        return None


def extract_offer_data(driver: WebDriver, field_selectors: dict[str, str]):
    """
    Parses the offer page and extracts relevant information.

    Args:
        driver (WebDriver): The WebDriver instance used to navigate the web page.
        field_selectors (dict[str, str]): A dictionary containing CSS selectors for different fields.

    Returns:
        dict: A dictionary containing the extracted information from the offer page.
    """
    offer_url = driver.current_url

    soup_offer = BeautifulSoup(driver.page_source, "html.parser")
    description = soup_offer.select_one(field_selectors["description"])

    record = {}
    record["link"]: dict[str, str] = offer_url

    # Get header and description data
    extract_data(
        field_selectors,
        ["title", "location", "price", "summary_description"],
        description,
        record,
    )

    # Get location
    location_paragraphs = soup_offer.select_one(field_selectors["location_paragraphs"])
    record["location"] = location_paragraphs.get("alt") if location_paragraphs else None

    # Get listing details
    listing_details = description.select(field_selectors["listing_details"])
    detail_fields = [
        "ownership",
        "floor_level",
        "is_furnished",
        "building_type",
        "square_meters",
        "number_of_rooms",
        "rent",
    ]
    record.update(
        {
            field: safe_get_text(detail)
            for field, detail in zip(detail_fields, listing_details)
        }
    )

    return record
