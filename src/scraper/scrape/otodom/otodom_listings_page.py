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
from config import SCRAPER
from scrape.otodom.otodom_offer_page import open_process_and_close_window


def page_offers_orchestrator(
    driver: WebDriver,
    search_criteria: dict[str, str | int],
    timestamp: str,
    progress: Counter,
):
    offers_cap: int = search_criteria["scraped_offers_cap"]

    if SCRAPER["anti_anti_bot"]:
        humans_delay(0.3, 0.5)

    set_max_offers_per_site(driver)

    if SCRAPER["anti_anti_bot"]:
        humans_delay(0.2, 0.4)

    await_for_offers_to_load(driver)

    # process for the first time
    process_page_offers(driver, search_criteria, timestamp, progress)

    if progress.count >= offers_cap:
        return

    next_page_selector = '[data-cy="pagination.next-page"]'

    while not is_disabled(driver, next_page_selector):
        await_for_offers_to_load(driver)

        if SCRAPER["anti_anti_bot"]:
            humans_delay(0.3, 0.5)

        process_page_offers(driver, search_criteria, timestamp, progress)

        if progress.count >= offers_cap:
            return

        click_next_page(driver)


def process_page_offers(
    driver: WebDriver, search_criteria: dict, timestamp: str, progress: Counter
):
    location_query = search_criteria["location_query"]
    offers_cap = search_criteria["scraped_offers_cap"]
    soup = BeautifulSoup(driver.page_source, "html.parser")

    listing_links = soup.find_all("a", {"data-cy": "listing-item-link"})

    original_window = driver.current_window_handle

    for sub_link in listing_links:
        if progress.count >= offers_cap:
            break

        open_process_and_close_window(
            driver, original_window, sub_link, location_query, timestamp, progress
        )


def await_for_offers_to_load(driver: WebDriver):
    main_feed_selector = '[role="main"]'
    WebDriverWait(driver, SCRAPER["multi_wait_timeout"]).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, main_feed_selector))
    )


def set_max_offers_per_site(driver: WebDriver):
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
    next_button_selector = '[data-cy="pagination.next-page"]'
    WebDriverWait(driver, SCRAPER["multi_wait_timeout"]).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, next_button_selector))
    )
    next_button = driver.find_element(By.CSS_SELECTOR, next_button_selector)
    next_button.click()


def is_disabled(driver: WebDriver, selector: str) -> bool:
    try:
        selector = f'{selector}[disabled=""]'

        driver.find_element(By.CSS_SELECTOR, selector)
        return True
    except NoSuchElementException:
        return False
