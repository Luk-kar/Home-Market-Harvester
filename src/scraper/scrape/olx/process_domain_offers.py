# Standard imports
import logging

# Third-party imports
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Local imports
from _utils import humans_delay
from config import SUBDOMAINS, LOGGING, SCRAPER
from scrape.olx.process_offer import process_offer as process_offer_olx
from scrape.otodom.process_offer import process_offer as process_offer_otodom
from scrape.custom_errors import OfferProcessingError


def process_domain_offers(driver: WebDriver):
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
            humans_delay()  # Human behavior

        driver.execute_script(f"window.open('{offer_url}', '_blank');")
        driver.switch_to.window(driver.window_handles[1])

        if subdomain["olx"] in offer_url:
            data = process_offer_olx(driver)

        elif subdomain["otodom"] in offer_url:
            data = process_offer_otodom(driver)

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
