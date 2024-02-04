"""
This module is responsible for extracting detailed information from real estate offer pages. 
It utilizes Selenium WebDriver for webpage navigation 
and BeautifulSoup for HTML content parsing. 
The module defines functions to process an offer page, 
extract key information using specific field selectors, 
and compile this information into a structured dictionary. 
It also includes robust error handling and logging and 
data extraction from offer pages.
"""

# Standard imports
from bs4 import BeautifulSoup
from selenium.webdriver.remote.webdriver import WebDriver
import logging

# Local imports
from pipeline.src.a_scraping._utils.selenium_utils import (
    wait_for_conditions,
    extract_data,
)
from pipeline.src.a_scraping.config import LOGGING
from pipeline.src.a_scraping.scrape.custom_errors import OfferProcessingError


def scrape_offer_page(driver: WebDriver) -> dict[str, str]:
    """
    Process an offer page and extract relevant information using the provided WebDriver.

    Args:
        driver (WebDriver): The WebDriver instance used to navigate
            and interact with the offer page.

    Returns:
        dict[str, str]: A dictionary containing the extracted information from the offer page.
            The keys represent the information categories,
            and the values represent the page selectors.
    """

    field_selectors = {
        "main_points": '[data-testid="ad.top-information.table"]',
        "additional_points": '[data-testid="ad.additional-information.table"]',
        "title": '[data-cy="adPageAdTitle"]',
        "location": '[data-testid="map-link-container"]',
        "price": '[data-cy="adPageHeaderPrice"]',
        "square_meters": '[data-testid="table-value-area"]',
        "rent": '[data-testid="table-value-rent"]',
        "number_of_rooms": '[data-testid="table-value-rooms_num"]',
        "deposit": '[data-testid="table-value-deposit"]',
        "floor_level": '[data-testid="table-value-floor"]',
        "building_type": '[data-testid="table-value-building_type"]',
        "available_from": '[data-testid="table-value-free_from"]',
        "balcony_garden_terrace": '[data-testid="table-value-outdoor"]',
        "remote service": '[aria-label="Obsługa zdalna"]',
        "completion": '[data-testid="table-value-construction_status"]',
        "summary_description": '[data-testid="content-container"]',
        "ownership": '[data-testid="table-value-advertiser_type"]',
        "rent_to_students": '[data-testid="table-value-rent_to_students"]',
        "equipment": '[data-testid="table-value-equipment_types"]',
        "media_types": '[data-testid="table-value-media_types"]',
        "heating": '[data-testid="table-value-heating"]',
        "security": '[data-testid="table-value-security_types"]',
        "windows": '[data-testid="table-value-windows_type"]',
        "elevator": '[data-testid="table-value-lift"]',
        "parking_space": '[data-testid="table-value-car"]',
        "build_year": '[data-testid="table-value-build_year"]',
        "building_material": '[data-testid="table-value-building_material"]',
        "additional_information": '[data-testid="table-value-extras_types"]',
    }

    conditions = [
        field_selectors[key]
        for key in [
            "main_points",
            "additional_points",
            "title",
            "location",
            "price",
            "summary_description",
        ]
    ]

    if wait_for_conditions(driver, *conditions):
        return extract_offer_content(driver, field_selectors)
    else:
        offer_url = driver.current_url
        logging.error("Failed to process: %s", offer_url)
        if LOGGING["debug"]:
            raise OfferProcessingError(offer_url, "Failed to process offer URL")
        return None


def extract_offer_content(driver: WebDriver, field_selectors: dict[str, str]):
    """
    Parses the offer details from the given web page using the provided field selectors.

    Args:
        driver (WebDriver): The web driver instance.
        field_selectors (dict[str, str]): A dictionary containing the field selectors for extracting data.

    Returns:
        dict[str, str]: A dictionary containing the parsed offer details.
    """

    offer_url = driver.current_url

    soup_offer = BeautifulSoup(driver.page_source, "html.parser")

    main_points = soup_offer.select_one('[data-testid="ad.top-information.table"]')
    additional_points = soup_offer.select_one(
        '[data-testid="ad.additional-information.table"]'
    )

    record: dict[str, str] = {}
    record["link"] = offer_url

    extract_data(
        field_selectors,
        ["title", "location", "price", "summary_description"],
        soup_offer,
        record,
    )

    extract_data(
        field_selectors,
        [
            "square_meters",
            "rent",
            "number_of_rooms",
            "deposit",
            "floor_level",
            "building_type",
            "available_from",
            "balcony_garden_terrace",
            "remote service",
            "completion",
        ],
        main_points,
        record,
    )

    extract_data(
        field_selectors,
        [
            "ownership",
            "rent_to_students",
            "equipment",
            "media_types",
            "heating",
            "security",
            "windows",
            "elevator",
            "parking_space",
            "build_year",
            "building_material",
            "additional_information",
        ],
        additional_points,
        record,
    )

    return record
