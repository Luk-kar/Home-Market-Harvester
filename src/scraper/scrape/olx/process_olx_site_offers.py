# Standard imports
import logging

# Third-party imports
from bs4 import BeautifulSoup
from enlighten import Counter
from requests.exceptions import RequestException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Local imports
from _utils.selenium_utils import humans_delay
from csv_manager import save_to_csv
from config import DOMAINS, LOGGING, SCRAPER
from scrape.olx.process_offer import process_offer as process_offer_olx
from scrape.otodom.extract_offer import extract_data as process_offer_otodom
from scrape.custom_errors import OfferProcessingError


def process_domain_offers_olx(
    driver: WebDriver, search_criteria: dict, timestamp: str, progress: Counter
):
    """
    Process the offers from the OLX domain and save them to a CSV file.

    Args:
        driver (WebDriver): The WebDriver instance for interacting with the browser.
        search_criteria (dict): The search criteria for filtering the offers.
        timestamp (str): The timestamp for the current scraping process.
        progress (Counter): The counter for tracking the progress of scraping.

    Returns:
        None
    """
    field_selectors = {
        "accept_cookies": "button[id='onetrust-accept-btn-handler']",
        "flat_offer_icon": '[data-testid="blueprint-card-param-icon"]',
        "offers_listings": '[data-testid="listing-grid"]',
        "offers": '[data-testid="l-card"]',
        "pagination_forward": '[data-testid="pagination-forward"]',
    }

    location_query = search_criteria["location_query"]
    offers_cap = search_criteria["scraped_offers_cap"]

    accept_cookies(driver, field_selectors)

    humans_delay(0.2, 0.4)

    while True:
        await_element(driver, field_selectors["offers_listings"])

        if not has_offer(driver, field_selectors["flat_offer_icon"]):
            break

        soup = BeautifulSoup(driver.page_source, "html.parser")
        offers_listings = soup.select_one(field_selectors["offers_listings"])
        offers = offers_listings.select(field_selectors["offers"])
        url_offers = extract_offer_urls(offers)

        for offer_url in url_offers:
            if progress.count >= offers_cap:
                break

            subdomain = {"olx": DOMAINS["olx"]["domain"], "otodom": DOMAINS["otodom"]}
            offer_url = normalize_offer_url(offer_url, subdomain["olx"])

            if SCRAPER["anti_anti_bot"]:
                humans_delay()  # Human behavior

            open_new_offer(driver, offer_url)

            if subdomain["olx"] in offer_url:
                process_olx_offer(
                    driver, location_query, subdomain["olx"], timestamp, progress
                )
            elif subdomain["otodom"] in offer_url:
                process_otodom_offer(
                    driver, location_query, subdomain["otodom"], timestamp, progress
                )
            else:
                raise RequestException(f"Unrecognized URL: {offer_url}")

            return_to_listing_page(driver)

        if not has_next_page(driver, field_selectors["pagination_forward"]):
            break
        else:
            click_next_page(driver, field_selectors["pagination_forward"])


def await_element(driver, selector):
    """
    Waits for an element to be present in the DOM using the given selector.

    Args:
        driver: The WebDriver instance.
        selector: A dictionary containing the CSS selector for the element.

    Returns:
        None
    """
    WebDriverWait(driver, SCRAPER["wait_timeout"]).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, selector["offers_listings"]))
    )


def accept_cookies(driver: WebDriver, field_selectors: dict[str, str]):
    """
    Accepts cookies on the website by clicking the accept cookies button.

    Args:
        driver (WebDriver): The WebDriver instance.
        field_selectors (dict[str, str]): Dictionary containing CSS selectors for different fields.

    Returns:
        None
    """
    WebDriverWait(driver, SCRAPER["wait_timeout"]).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, field_selectors["accept_cookies"])
        )
    )

    button_accept_cookies = driver.find_element(
        By.CSS_SELECTOR, field_selectors["accept_cookies"]
    )
    button_accept_cookies.click()


def return_to_listing_page(driver: WebDriver):
    """
    Closes the current window and switches back to the main listing page.

    Args:
        driver (WebDriver): The WebDriver instance.

    Returns:
        None
    """
    driver.close()
    driver.switch_to.window(driver.window_handles[0])


def open_new_offer(driver: WebDriver, offer_url: str):
    """
    Opens a new offer in a new tab/window using the provided WebDriver instance.

    Args:
        driver (WebDriver): The WebDriver instance to use for opening the offer.
        offer_url (str): The URL of the offer to open.

    Returns:
        None
    """
    driver.execute_script(f"window.open('{offer_url}', '_blank');")
    driver.switch_to.window(driver.window_handles[1])


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


def has_next_page(driver: WebDriver, selector: str) -> bool:
    """
    Check if there is a next page button.

    Args:
        driver (WebDriver): The WebDriver instance for interacting with the browser.
        selector (str): The CSS selector for identifying the next page button.

    Returns:
        bool: True if a next page button is found, False otherwise.
    """
    next_page_button = driver.find_element(By.CSS_SELECTOR, selector)
    return bool(next_page_button)


def click_next_page(driver: WebDriver, selector: str):
    """
    Click the next page button.

    Args:
        driver (WebDriver): The WebDriver instance for interacting with the browser.
        selector (str): The CSS selector for identifying the next page button.

    Returns:
        None
    """

    wait = WebDriverWait(driver, SCRAPER["wait_timeout"])
    next_page_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
    )

    try:
        scroll_into_element = "arguments[0].scrollIntoView();"
        driver.execute_script(scroll_into_element, next_page_button)

        next_page_button.click()

    except Exception as e:
        javascript_click = "arguments[0].click();"
        driver.execute_script(javascript_click, next_page_button)
