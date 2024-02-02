"""
This module manages the scraping of real estate offers from the Otodom website. 
It includes functionality to filter offers based on user-defined search criteria, 
handle cookie acceptance, and navigate the Otodom interface. 
The module uses Selenium WebDriver for webpage interaction, 
automating tasks like selecting transaction types, 
setting search radius, entering location queries, 
and advancing through offer listings. 
Functions are designed to streamline the process of setting up a scraping session and 
ensure that relevant offers are captured and processed.
"""

# Standard imports
import re

# Third-party imports
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver

# Local imports
from pipeline.src.scraper._utils.selenium_utils import await_element, humans_delay
from pipeline.src.scraper.config import SCRAPER
from pipeline.src.scraper.scrape.otodom.otodom_listings_page import (
    page_offers_orchestrator,
)


def process_domain_offers_otodom(
    driver: WebDriver,
    search_criteria: dict[str, str | int],
    timestamp: str,
    progress: object,
    scraped_urls: set[str],
):
    """
    Process domain offers from Otodom.

    Args:
        driver (WebDriver): The WebDriver instance for interacting with the web page.
        search_criteria (dict[str, str | int]): The search criteria for filtering the offers.
        timestamp (str): The timestamp of the scraping process.
        progress (object): The progress object for tracking the scraping progress.
        scraped_urls (set[str]): The set of scraped URLs.

    Returns:
        None
    """
    location: str = search_criteria["location_query"]
    km: int = search_criteria["area_radius"]

    search_offers(driver, location, km)
    page_offers_orchestrator(driver, search_criteria, timestamp, progress, scraped_urls)


def search_offers(driver: WebDriver, location_query_input: str, km: int):
    """
    Search for offers on the Otodom website based on the provided location and distance radius.

    Args:
        driver (WebDriver): The WebDriver instance used for web scraping.
        location_query_input (str): The location query input.
        km (int): The distance radius in kilometers.

    Returns:
        None
    """
    field_selectors = {
        "cookies_banner": '[id="onetrust-banner-sdk"]',
        "accept_cookies": '[id="onetrust-accept-btn-handler"]',
        "user_form": '[data-testid="form-wrapper"]',
        "transaction_type": '[data-cy="search-form--field--transaction"]',
        "for_rent": "#react-select-transaction-option-0",
        "location": '[data-testid="search.form.location.button"]',
        "location_input": "location-picker-input",
        "location_dropdown": '[data-testid="search.form.location.container"]',
        "location_suggestions": 'li[data-testid="suggestions-item"]',
        "distance_radius": '[data-cy="search-form--field--distanceRadius"]',
        "distance_radius_dropdown": 'div[data-cy="search.form.location.dropdown.list-wrapper"]',
        "distance_radius_options": "react-select-distanceRadius-listbox",
        "distance_radius_suggestions": "li[data-testid='suggestions-item']",
    }

    accept_cookies(driver, field_selectors)

    if SCRAPER["anti_anti_bot"]:
        humans_delay(0.15, 0.2)

    select_for_rent_option(driver, field_selectors)

    if SCRAPER["anti_anti_bot"]:
        humans_delay(0.15, 0.4)

    select_distance_radius(driver, field_selectors, km)

    if SCRAPER["anti_anti_bot"]:
        humans_delay(0.3, 0.5)

    write_location(driver, field_selectors, location_query_input)

    if SCRAPER["anti_anti_bot"]:
        humans_delay(0.3, 0.5)

    press_find_offers_button(driver)


def accept_cookies(driver: WebDriver, field_selectors: dict[str, str]):
    """
    Accepts cookies on the webpage.

    Args:
        driver (WebDriver): The WebDriver instance used to interact with the webpage.
        field_selectors (dict[str, str]): A dictionary containing CSS selectors for various fields on the webpage.

    Returns:
        None
    """
    await_element(
        driver, field_selectors["cookies_banner"], timeout=SCRAPER["multi_wait_timeout"]
    )

    accept_cookies_button = driver.find_element(
        By.CSS_SELECTOR,
        f"{field_selectors['cookies_banner']} {field_selectors['accept_cookies']}",
    )
    if SCRAPER["anti_anti_bot"]:
        humans_delay(0.2, 0.4)
    accept_cookies_button.click()


def select_for_rent_option(driver: WebDriver, field_selectors: dict[str, str]):
    """
    Selects the 'For Rent' option in the transaction type field on the main page of Otodom website.

    Args:
        driver (WebDriver): The WebDriver instance used to interact with the web page.
        field_selectors (dict[str, str]): A dictionary containing CSS selectors for different fields.

    Returns:
        None
    """
    await_element(
        driver,
        field_selectors["user_form"],
        timeout=SCRAPER["multi_wait_timeout"],
    )
    user_form = driver.find_element(
        By.CSS_SELECTOR,
        field_selectors["user_form"],
    )
    transaction_type = user_form.find_element(
        By.CSS_SELECTOR,
        field_selectors["transaction_type"],
    )
    transaction_type.click()

    await_element(
        driver,
        field_selectors["for_rent"],
        timeout=SCRAPER["multi_wait_timeout"],
    )
    transaction_type.find_element(By.CSS_SELECTOR, field_selectors["for_rent"]).click()


def select_distance_radius(driver: WebDriver, field_selectors: dict[str, str], km: int):
    """
    Selects the distance radius option on the main page of the Otodom website.

    Args:
        driver (WebDriver): The WebDriver instance.
        field_selectors (dict[str, str]): A dictionary containing CSS selectors for the fields on the page.
        km (int): The distance radius in kilometers.

    Returns:
        None
    """
    distance_dropdown = {
        # Km : index
        0: 0,
        5: 1,
        10: 2,
        15: 3,
        25: 4,
        50: 5,
        75: 6,
    }

    select_option = distance_dropdown[km]

    distance_radius_element = driver.find_element(
        By.CSS_SELECTOR, field_selectors["distance_radius"]
    )
    distance_radius_element.click()
    await_element(
        driver,
        field_selectors["distance_radius_options"],
        by=By.ID,
        timeout=SCRAPER["multi_wait_timeout"],
    )

    distance_radius_options_element = driver.find_element(
        By.ID, field_selectors["distance_radius_options"]
    )

    div_elements = distance_radius_options_element.find_elements(By.TAG_NAME, "div")

    # Regular expression pattern to match the IDs
    pattern = re.compile(r"react-select-distanceRadius-option-\d+")

    # Filter elements based on the pattern
    matching_elements = [
        element
        for element in div_elements
        if pattern.match(element.get_attribute("id"))
    ]

    matching_elements[select_option].click()


def write_location(
    driver: WebDriver, field_selectors: dict[str, str], location_query_input: str
):
    """
    Writes the location query input in the location field of the webpage.

    Args:
        driver (WebDriver): The WebDriver instance.
        field_selectors (dict[str, str]): A dictionary containing CSS selectors for different fields.
        location_query_input (str): The location query input to be written.

    Returns:
        None
    """
    location_element = driver.find_element(By.CSS_SELECTOR, field_selectors["location"])
    location_element.click()

    if SCRAPER["anti_anti_bot"]:
        humans_delay(0.2, 0.4)

    await_element(
        driver,
        field_selectors["location_input"],
        By.ID,
        timeout=SCRAPER["multi_wait_timeout"],
    )
    input_element = driver.find_element(By.ID, field_selectors["location_input"])
    input_element.send_keys(location_query_input)

    await_element(
        driver,
        field_selectors["location_dropdown"],
        timeout=SCRAPER["multi_wait_timeout"],
    )
    location_dropdown = driver.find_element(
        By.CSS_SELECTOR, field_selectors["location_dropdown"]
    )

    await_element(
        driver,
        field_selectors["location_suggestions"],
        timeout=SCRAPER["multi_wait_timeout"],
    )
    suggestions = location_dropdown.find_elements(
        By.CSS_SELECTOR, field_selectors["location_suggestions"]
    )

    closest_match = suggestions[0]
    closest_match.click()


def press_find_offers_button(driver: WebDriver):
    """
    Presses the 'Find Offers' button on the main page.

    Args:
        driver (WebDriver): The WebDriver instance.

    Returns:
        None
    """
    ActionChains(driver).send_keys(Keys.ENTER).perform()
