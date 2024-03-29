"""
This module provides functionality for orchestrating the scraping process of real estate offers 
from a single page on the Otodom website. 
It includes routines for processing each offer on the page, 
navigating through pagination, setting the maximum number of offers per page, 
and handling offer details. 
The module utilizes Selenium WebDriver for web page interactions 
and BeautifulSoup for parsing HTML content. 
Functions are included to manage page elements, 
such as checking for the existence of offers, 
clicking through pages, and ensuring the page's content has loaded.
"""

# Standard imports
from typing import Any

# Third-party imports
from bs4 import BeautifulSoup
from enlighten import Counter
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

# Local imports
from pipeline.stages.a_scraping._utils.selenium_utils import await_element, humans_delay
from pipeline.config.a_scraping import SCRAPER, DOMAINS
from pipeline.stages.a_scraping.scrape.otodom.otodom_offer_page import (
    open_process_and_close_window,
)


def page_offers_orchestrator(
    driver: WebDriver,
    search_criteria: dict[str, str | int],
    timestamp: str,
    progress: Counter,
    scraped_urls: set[str],
):
    """
    Orchestrates the scraping of offers from a single page on the Otodom website.

    Args:
        driver (WebDriver): The WebDriver instance for interacting with the web page.
        search_criteria (dict[str, str | int]): The search criteria used for filtering the offers.
        timestamp (str): The timestamp of the scraping process.
        progress (Counter): The counter to keep track of the number of scraped offers.
        scraped_urls (set[str]): The set of scraped URLs.

    Returns:
        None
    """

    field_selectors = {
        "next_page": 'ul[data-testid="frontend.search.base-pagination.nexus-pagination"] li[title="Go to next Page"]',
        "radius": '[data-cy="filter-distance-input"]',
        "listing_links": {"name": "a", "attrs": {"data-cy": "listing-item-link"}},
        "main_feed": '[role="main"]',
        "offers_per_page": "react-select-entriesPerPage-live-region",
        "offers_per_page_dropdown": "react-select-entriesPerPage-input",
        "offers_per_page_list": "react-select-entriesPerPage-listbox",
        "highest_per_page_option": "div[id^='react-select-entriesPerPage-option-']",
    }

    offers_cap: int = search_criteria["scraped_offers_cap"]

    if SCRAPER["anti_anti_bot"]:
        humans_delay(0.3, 0.5)

    set_max_offers_per_site(driver, field_selectors)

    if SCRAPER["anti_anti_bot"]:
        humans_delay(0.2, 0.4)

    while True:
        await_for_offers_to_load(driver, field_selectors["main_feed"])

        if SCRAPER["anti_anti_bot"]:
            humans_delay(0.3, 0.5)

        process_page_offers(
            driver,
            field_selectors["listing_links"],
            search_criteria,
            timestamp,
            progress,
            scraped_urls,
        )

        if progress.count >= offers_cap:
            break

        if is_element(driver, field_selectors["next_page"]):
            click_next_page(driver, field_selectors["next_page"])
        else:
            break


def process_page_offers(
    driver: WebDriver,
    offers_links_selector: dict[str, str | dict[str, str]],
    search_criteria: dict,
    timestamp: str,
    progress: Counter,
    scraped_urls: set[str],
):
    """
    Process the offers on the page.

    Args:
        driver (WebDriver): The WebDriver instance.
        offers_links_selector (dict[str, str | dict[str, str]]): The CSS selector for the offers links.
        search_criteria (dict): The search criteria.
        timestamp (str): The timestamp of the scraping process.
        progress (Counter): The progress counter.
        scraped_urls (set[str]): The set of scraped URLs.

    Returns:
        None
    """
    location_query = search_criteria["location_query"]
    offers_cap = search_criteria["scraped_offers_cap"]
    soup = BeautifulSoup(driver.page_source, "html.parser")

    offers_links = soup.find_all(**offers_links_selector)

    original_window = driver.current_window_handle

    for link_offer in offers_links:
        if progress.count >= offers_cap:
            break

        if DOMAINS["otodom"] + link_offer["href"] in scraped_urls:
            continue

        open_process_and_close_window(
            driver,
            original_window,
            link_offer["href"],
            location_query,
            timestamp,
            progress,
            scraped_urls,
        )


def await_for_offers_to_load(driver: WebDriver, selector: str):
    """
    Waits for the offers to load on the page.

    Args:
        driver (WebDriver): The WebDriver instance.
        selector (str): The CSS selector of the element to wait for.

    Returns:
        None
    """
    await_element(driver, selector, timeout=SCRAPER["multi_wait_timeout"])


def set_max_offers_per_site(driver: WebDriver, field_selectors: dict[str, Any]):
    """
    Sets the maximum number of offers per site in the Otodom listings page.

    Args:
        driver (WebDriver): The WebDriver instance.
        field_selectors (dict[str, Any]): The field selectors.

    Returns:
        None
    """
    pagination_input_selector = field_selectors["offers_per_page"]
    await_element(
        driver,
        pagination_input_selector,
        by=By.ID,
        timeout=SCRAPER["multi_wait_timeout"],
    )
    pagination_input_element = driver.find_element(By.ID, pagination_input_selector)
    pagination_container = pagination_input_element.find_element(By.XPATH, "./..")
    pagination_container.click()

    dropdown_list_selector = field_selectors["offers_per_page_list"]
    await_element(
        driver, dropdown_list_selector, by=By.ID, timeout=SCRAPER["multi_wait_timeout"]
    )
    offers_dropdown_list = driver.find_element(By.ID, dropdown_list_selector)

    dropdown_options = offers_dropdown_list.find_elements(
        By.CSS_SELECTOR, field_selectors["highest_per_page_option"]
    )
    highest_option = dropdown_options[-1] if dropdown_options else None

    if highest_option:
        # If there is at least one option, interact with the last one
        highest_option.click()
    else:
        raise NoSuchElementException(
            "No options found in the offers per page dropdown."
        )


def click_next_page(driver: WebDriver, selector: str):
    """
    Clicks on the next page button in the Otodom listings page.

    Args:
        driver (WebDriver): The WebDriver instance used for scraping.
        selector (str): The CSS selector of the next page button.

    Returns:
        None

    Raises:
        TimeoutException: If the next page button is not found.
        NoSuchElementException: If the next page button is not found.
        Exception: If an unexpected error occurs.
    """

    def get_error_message(selector, e):
        return "Selector:\n" f"{selector}\n" "Error:" f"{e}"

    try:
        await_element(driver, selector, timeout=SCRAPER["multi_wait_timeout"])
        next_button = driver.find_element(By.CSS_SELECTOR, selector)
        next_button.click()
    except TimeoutException as e:
        raise TimeoutException(
            "Timeout waiting for next page button.\n"
            f"{get_error_message(selector, e)}"
        )
    except NoSuchElementException as e:
        raise NoSuchElementException(
            "Next page button not found." f"{get_error_message(selector, e)}"
        )
    except Exception as e:
        raise Exception(
            f"Unexpected error clicking next page.\n"
            f"{get_error_message(selector, e)}"
        )


def is_element(driver: WebDriver, selector: str) -> bool:
    """
    Checks if an element is present on the page.

    Args:
        driver (WebDriver): The WebDriver instance.
        selector (str): The CSS selector of the element.

    Returns:
        bool: True if the element is present, False otherwise.
    """
    try:
        await_element(driver, selector, timeout=SCRAPER["multi_wait_timeout"])
        driver.find_element(By.CSS_SELECTOR, selector)
        return True

    except NoSuchElementException:
        return False
