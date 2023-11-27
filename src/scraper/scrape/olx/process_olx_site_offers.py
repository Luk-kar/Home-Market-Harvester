# Standard imports
import logging

# Third-party imports
from bs4 import BeautifulSoup
from enlighten import Counter
from requests.exceptions import RequestException
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
    location_query = search_criteria["location_query"]
    offers_cap = search_criteria["scraped_offers_cap"]

    WebDriverWait(driver, SCRAPER["wait_timeout"]).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '[data-testid="listing-grid"]')
        )
    )

    soup = BeautifulSoup(driver.page_source, "html.parser")

    offers_listings = soup.select_one('[data-testid="listing-grid"]')
    offers = offers_listings.select('[data-testid="l-card"]')
    url_offers = []

    for offer in offers:
        first_anchor_tag = offer.select_one("a")

        if first_anchor_tag:
            href_link = first_anchor_tag["href"]
            url_offers.append(href_link)
        else:
            offer_id = offer["id"] if "id" in offer.attrs else "Unknown"
            logging.info("No link found in the offer with id=%s", offer_id)

    for offer_url in url_offers:
        if progress.count >= offers_cap:
            break

        subdomain = {"olx": DOMAINS["olx"]["domain"], "otodom": DOMAINS["otodom"]}
        if not offer_url.startswith("http"):
            offer_url = subdomain["olx"] + offer_url

        if SCRAPER["anti_anti_bot"]:
            humans_delay()  # Human behavior

        driver.execute_script(f"window.open('{offer_url}', '_blank');")
        driver.switch_to.window(driver.window_handles[1])

        if subdomain["olx"] in offer_url:
            record = process_offer_olx(driver)
            if record:
                save_to_csv(record, location_query, subdomain["olx"], timestamp)
                progress.update()
            else:
                logging.error("Failed to process: %s", offer_url)
                if LOGGING["debug"]:
                    raise OfferProcessingError(offer_url, "Failed to process offer URL")

        elif subdomain["otodom"] in offer_url:
            record = process_offer_otodom(driver)
            if record:
                save_to_csv(record, location_query, subdomain["otodom"], timestamp)
                progress.update()
            else:
                logging.error("Failed to process: %s", offer_url)
                if LOGGING["debug"]:
                    raise OfferProcessingError(offer_url, "Failed to process offer URL")

        else:
            raise RequestException(f"Unrecognized URL: {offer_url}")

        driver.close()
        driver.switch_to.window(driver.window_handles[0])
