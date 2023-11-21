# Standard imports
import logging

# Third-party imports
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Local imports
from _utils import random_delay
from config import SUBDOMAINS, LOGGING, SCRAPER
from scrape.olx_offer import get_offer_from_olx
from scrape.otodom_offer import get_offer_from_otodom


class OfferProcessingError(Exception):
    """Exception raised for errors in processing offer URLs."""

    def __init__(self, url, message="Error processing offer URL"):
        self.url = url
        self.message = f"{message}: {url}"
        super().__init__(self.message)

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message}"


def scrape_offers(url, driver):
    try:
        try:
            driver.get(url)
        except WebDriverException as e:
            # Attempt to refresh the page or handle the error as needed
            if LOGGING["debug"]:
                raise e

            logging.error("Connection issue encountered: %s", e)
            driver.refresh()

        if SUBDOMAINS["olx"] in url:
            extracts_page_offers_olx(driver)
        elif SUBDOMAINS["otodom"] in url:
            extracts_page_offers_otodom(driver)
            pass
        else:
            raise RequestException(f"Unrecognized URL: {url}")

    except Exception as e:
        if LOGGING["debug"]:
            raise e

        logging.error("Error occurred: %s", e)


def extracts_page_offers_olx(driver: WebDriver):
    WebDriverWait(driver, 10).until(
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
        subdomain = {"olx": SUBDOMAINS["olx"], "otodom": SUBDOMAINS["otodom"]}
        if not offer_url.startswith("http"):
            offer_url = subdomain["olx"] + offer_url

        if SCRAPER["anti-anti-bot"]:
            random_delay()  # Human behavior

        driver.execute_script(f"window.open('{offer_url}', '_blank');")
        driver.switch_to.window(driver.window_handles[1])

        if subdomain["olx"] in offer_url:
            data = get_offer_from_olx(driver)

        elif subdomain["otodom"] in offer_url:
            data = get_offer_from_otodom(driver)

        else:
            raise RequestException(f"Unrecognized URL: {offer_url}")

        if data is None:
            if LOGGING["debug"]:
                raise OfferProcessingError(offer_url, "Failed to process offer URL")

            logging.error("Failed to process: %s", offer_url)

        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        break  # todo

    print(data)  # todo


def extracts_page_offers_otodom(driver: WebDriver):
    WebDriverWait(driver, 10).until(
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
        subdomain = {"olx": SUBDOMAINS["olx"], "otodom": SUBDOMAINS["otodom"]}
        if not offer_url.startswith("http"):
            offer_url = subdomain["olx"] + offer_url

        if SCRAPER["anti-anti-bot"]:
            random_delay()  # Human behavior

        driver.execute_script(f"window.open('{offer_url}', '_blank');")
        driver.switch_to.window(driver.window_handles[1])

        if subdomain["olx"] in offer_url:
            data = get_offer_from_olx(driver)

        elif subdomain["otodom"] in offer_url:
            data = get_offer_from_otodom(driver)

        else:
            raise RequestException(f"Unrecognized URL: {offer_url}")

        if data is None:
            if LOGGING["debug"]:
                raise OfferProcessingError(offer_url, "Failed to process offer URL")

            logging.error("Failed to process: %s", offer_url)

        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        break  # todo

    print(data)  # todo
