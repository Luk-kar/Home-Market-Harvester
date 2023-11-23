# Standard imports
import logging

# Third-party imports
from requests.exceptions import RequestException
from selenium.common.exceptions import WebDriverException


# Local imports
from config import SUBDOMAINS, LOGGING
from scrape.olx.process_page_offers import (
    process_page_offers as process_page_offers_olx,
)
from scrape.otodom.process_page_offers import (
    process_page_offers as process_page_offers_otodom,
)


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
            process_page_offers_olx(driver)
        elif SUBDOMAINS["otodom"] in url:
            process_page_offers_otodom(driver)
            pass
        else:
            raise RequestException(f"Unrecognized URL: {url}")

    except Exception as e:
        if LOGGING["debug"]:
            raise e

        logging.error("Error occurred: %s", e)
