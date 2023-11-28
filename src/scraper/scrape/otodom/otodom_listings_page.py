# Standard imports
from typing import Any

# Third-party imports
from bs4 import BeautifulSoup
from enlighten import Counter
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

# Local imports
from _utils.selenium_utils import await_element, humans_delay
from config import SCRAPER, DOMAINS
from scrape.otodom.otodom_offer_page import open_process_and_close_window


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
        "next_page": '[data-cy="pagination.next-page"]',
        "radius": '[data-cy="filter-distance-input"]',
        "listing_links": {"name": "a", "attrs": {"data-cy": "listing-item-link"}},
        "main_feed": '[role="main"]',
        "offers_per_page": "react-select-entriesPerPage-input",
        "offers_per_page_dropdown": "react-select-entriesPerPage-input",
        "offers_per_page_list": "react-select-entriesPerPage-listbox",
        "highest_per_page_option": ".react-select__menu-list > .react-select__option:last-child",
        "next_page": '[data-cy="pagination.next-page"]',
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

        if not is_disabled(driver, field_selectors["next_page"]):
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
    input_per_page_selector = field_selectors["offers_per_page"]
    await_element(
        driver,
        input_per_page_selector,
        by=By.ID,
        timeout=SCRAPER["multi_wait_timeout"],
    )
    input_per_page = driver.find_element(By.ID, input_per_page_selector)
    input_per_page.click()

    dropdown_selector = field_selectors["offers_per_page_list"]
    await_element(
        driver, dropdown_selector, by=By.ID, timeout=SCRAPER["multi_wait_timeout"]
    )
    offers_per_page_list = driver.find_element(By.ID, dropdown_selector)

    last_option_element = offers_per_page_list.find_element(
        By.CSS_SELECTOR, field_selectors["highest_per_page_option"]
    )
    last_option_element.click()


def click_next_page(driver: WebDriver, selector: str):
    """
    Clicks on the next page button in the Otodom listings page.

    Args:
        driver (WebDriver): The WebDriver instance used for scraping.
        selector (str): The CSS selector of the next page button.

    Returns:
        None
    """
    await_element(driver, selector, timeout=SCRAPER["multi_wait_timeout"])
    next_button = driver.find_element(By.CSS_SELECTOR, selector)
    next_button.click()


def is_disabled(driver: WebDriver, selector: str) -> bool:
    """
    Check if a clickable element with the given selector is disabled.

    Args:
        driver (WebDriver): The WebDriver instance.
        selector (str): The CSS selector of the element.

    Returns:
        bool: True if the element is disabled, False otherwise.
    """
    try:
        selector = f'{selector}[disabled=""]'

        driver.find_element(By.CSS_SELECTOR, selector)
        return True
    except NoSuchElementException:
        return False
