# Third-party imports
from bs4 import BeautifulSoup
from enlighten import Counter
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Local imports
from _utils.selenium_utils import humans_delay
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
    offers_cap: int = search_criteria["scraped_offers_cap"]

    if SCRAPER["anti_anti_bot"]:
        humans_delay(0.3, 0.5)

    set_max_offers_per_site(driver)

    if SCRAPER["anti_anti_bot"]:
        humans_delay(0.2, 0.4)

    while True:
        await_for_offers_to_load(driver)

        if SCRAPER["anti_anti_bot"]:
            humans_delay(0.3, 0.5)

        process_page_offers(driver, search_criteria, timestamp, progress, scraped_urls)

        if progress.count >= offers_cap:
            break

        next_page_selector = '[data-cy="pagination.next-page"]'
        if not is_disabled(driver, next_page_selector):
            click_next_page(driver)
        else:
            break


def process_page_offers(
    driver: WebDriver,
    search_criteria: dict,
    timestamp: str,
    progress: Counter,
    scraped_urls: set[str],
):
    """
    Process the offers on the page.

    Args:
        driver (WebDriver): The WebDriver instance.
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

    listing_links = soup.find_all("a", {"data-cy": "listing-item-link"})

    original_window = driver.current_window_handle

    for sub_link in listing_links:
        if progress.count >= offers_cap:
            break

        if DOMAINS["otodom"] + sub_link["href"] in scraped_urls:
            continue

        open_process_and_close_window(
            driver,
            original_window,
            sub_link,
            location_query,
            timestamp,
            progress,
            scraped_urls,
        )


def await_for_offers_to_load(driver: WebDriver):
    """
    Waits for the offers to load on the page.

    Args:
        driver (WebDriver): The WebDriver instance.

    Returns:
        None
    """
    main_feed_selector = '[role="main"]'
    WebDriverWait(driver, SCRAPER["multi_wait_timeout"]).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, main_feed_selector))
    )


def set_max_offers_per_site(driver: WebDriver):
    """
    Sets the maximum number of offers per site in the Otodom listings page.

    Args:
        driver (WebDriver): The WebDriver instance.

    Returns:
        None
    """
    entries_id = "react-select-entriesPerPage-input"
    WebDriverWait(driver, SCRAPER["multi_wait_timeout"]).until(
        EC.element_to_be_clickable((By.ID, entries_id))
    )
    entries_per_page = driver.find_element(By.ID, entries_id)
    entries_per_page.click()

    entries_per_page_id = "react-select-entriesPerPage-listbox"
    WebDriverWait(driver, SCRAPER["multi_wait_timeout"]).until(
        EC.element_to_be_clickable((By.ID, entries_per_page_id))
    )
    entries_per_page_listbox = driver.find_element(By.ID, entries_per_page_id)

    last_option_selector = ".react-select__menu-list > .react-select__option:last-child"
    last_option_element = entries_per_page_listbox.find_element(
        By.CSS_SELECTOR, last_option_selector
    )
    last_option_element.click()


def click_next_page(driver: WebDriver):
    """
    Clicks on the next page button in the Otodom listings page.

    Args:
        driver (WebDriver): The WebDriver instance used for scraping.

    Returns:
        None
    """
    next_button_selector = '[data-cy="pagination.next-page"]'
    WebDriverWait(driver, SCRAPER["multi_wait_timeout"]).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, next_button_selector))
    )
    next_button = driver.find_element(By.CSS_SELECTOR, next_button_selector)
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
