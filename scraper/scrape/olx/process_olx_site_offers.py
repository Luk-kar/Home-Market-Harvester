# Third-party imports
from bs4 import BeautifulSoup
from enlighten import Counter
from requests.exceptions import RequestException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver


# Local imports
from scraper._utils.selenium_utils import await_element, humans_delay
from scraper.config import DOMAINS, SCRAPER
from scraper.scrape.olx.offer_utils import (
    extract_offer_urls,
    has_offer,
    normalize_offer_url,
    has_next_page,
)
from scraper.scrape.olx.navigation import (
    click_next_page,
    open_new_offer,
    return_to_listing_page,
)
from scraper.scrape.olx.domain_offer_processor import (
    process_olx_offer,
    process_otodom_offer,
)


def process_domain_offers_olx(
    driver: WebDriver,
    search_criteria: dict,
    timestamp: str,
    progress: Counter,
    scraped_urls: set[str],
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

    accept_cookies(driver, field_selectors["accept_cookies"])

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

            scaped_url = None

            if subdomain["olx"] in offer_url:
                if offer_url in scraped_urls:
                    return_to_listing_page(driver)
                    continue

                scaped_url = process_olx_offer(
                    driver, location_query, subdomain["olx"], timestamp, progress
                )

            elif subdomain["otodom"] in offer_url:
                if offer_url in scraped_urls:
                    return_to_listing_page(driver)
                    continue

                scaped_url = process_otodom_offer(
                    driver, location_query, subdomain["otodom"], timestamp, progress
                )

            else:
                raise RequestException(f"Unrecognized URL: {offer_url}")

            scraped_urls.add(scaped_url)

            return_to_listing_page(driver)

        if not has_next_page(driver, field_selectors["pagination_forward"]):
            break
        else:
            click_next_page(driver, field_selectors["pagination_forward"])


def accept_cookies(driver: WebDriver, selector: str):
    """
    Accepts cookies on the website by clicking the accept cookies button.

    Args:
        driver (WebDriver): The WebDriver instance.
        selector (str): The CSS selector for the accept cookies button.

    Returns:
        None
    """

    await_element(driver, selector)

    button_accept_cookies = driver.find_element(By.CSS_SELECTOR, selector)
    button_accept_cookies.click()
