# Standard imports
import logging
import urllib.parse
import datetime

# Third-party imports
from requests.exceptions import RequestException
from selenium.common.exceptions import WebDriverException


# Local imports
from config import SUBDOMAINS, LOGGING, SCRAPER
from scrape.olx.process_domain_offers import (
    process_domain_offers as process_domain_offers_olx,
)
from scrape.otodom.process_domain_offers import (
    process_domain_offers as process_domain_offers_otodom,
)


def transform_location_to_url_format(location: str) -> str:
    formatted_location = location.replace(" ", "-")

    encoded_location = urllib.parse.quote(formatted_location, safe="-")

    return encoded_location


def scrape_offers(driver, location_query: str, km: int):
    try:
        formatted_location = transform_location_to_url_format(location_query)
        urls = [
            f'{SUBDOMAINS["olx"]}/{SCRAPER["category"]}q-{formatted_location}/',
            SUBDOMAINS["otodom"],
        ]
        timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

        for url in urls:
            try:
                driver.get(url)
            except WebDriverException as e:
                # Attempt to refresh the page or handle the error as needed
                if LOGGING["debug"]:
                    raise e

                logging.error("Connection issue encountered: %s", e)
                driver.refresh()

            if SUBDOMAINS["olx"] in url:
                process_domain_offers_olx(driver, timestamp, location_query)
            elif SUBDOMAINS["otodom"] in url:
                process_domain_offers_otodom(driver, location_query, km, timestamp)
                pass
            else:
                raise RequestException(f"Unrecognized URL: {url}")

    except Exception as e:
        if LOGGING["debug"]:
            raise e

        logging.error("Error occurred: %s", e)
