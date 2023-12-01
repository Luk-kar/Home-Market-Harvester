from _utils import random_delay
from config import SCRAPER, SUBDOMAINS
from bs4 import BeautifulSoup
from scrape.olx_offer import get_offer_from_olx
from scrape.otodom_offer import get_offer_from_otodom

from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException

import logging


def scrape_offers(url, driver):
    try:
        try:
            driver.get(url)
        except WebDriverException as e:
            # Attempt to refresh the page or handle the error as needed
            logging.error(f"Connection issue encountered: {e}")
            driver.refresh()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[data-testid="listing-grid"]')
            )
        )

        soup = BeautifulSoup(driver.page_source, "html.parser")
        offers_listings = soup.select_one('[data-testid="listing-grid"]')

        offers = offers_listings.select('[data-testid="l-card"]')
        url_offers = []
        data = None

        for offer in offers:
            first_anchor_tag = offer.select_one("a")

            if first_anchor_tag:
                href_link = first_anchor_tag["href"]
                url_offers.append(href_link)
            else:
                offer_id = offer["id"] if "id" in offer.attrs else "Unknown"
                logging.info(f"No link found in the offer with id={offer_id}")

        for offer_url in url_offers:
            subdomain = {"olx": SCRAPER["domain"], "otodom": SUBDOMAINS["otodom"]}
            if not offer_url.startswith("http"):
                offer_url = SCRAPER["domain"] + offer_url

            random_delay()  # Human behavior, anti-anti-bot

            driver.execute_script(f"window.open('{offer_url}', '_blank');")
            driver.switch_to.window(driver.window_handles[1])

            if subdomain["olx"] in offer_url:
                data = get_offer_from_olx(offer_url, driver)

            elif subdomain["otodom"] in offer_url:
                data = get_offer_from_otodom(offer_url, driver)

            else:
                raise RequestException(f"Unrecognized URL: {offer_url}")

            if data is None:
                logging.error(f"Failed to process {offer_url}: {e}")

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            break

        return data

    except Exception as e:
        logging.error(f"Error occurred: {e}")
