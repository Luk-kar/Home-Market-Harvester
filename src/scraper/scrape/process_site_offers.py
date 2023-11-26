# Standard imports
import logging
import urllib.parse
import datetime

# Third-party imports
from requests.exceptions import RequestException
from selenium.common.exceptions import WebDriverException


# Local imports
from _utils import humans_delay
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


def scrape_offers(driver, website_arguments):
    try:
        location_query = website_arguments["location"]
        formatted_location = transform_location_to_url_format(location_query)
        urls = [
            f'{SUBDOMAINS["olx"]}/{SCRAPER["category"]}q-{formatted_location}/',
            SUBDOMAINS["otodom"],
        ]
        timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

        for url in urls:
            humans_delay()
            try:
                driver.get(url)
            except WebDriverException as e:
                # Attempt to refresh the page or handle the error as needed
                if LOGGING["debug"]:
                    raise e

                logging.error("Connection issue encountered: %s", e)
                driver.refresh()

            if SUBDOMAINS["olx"] in url:
                process_domain_offers_olx(driver, location_query, timestamp)
            elif SUBDOMAINS["otodom"] in url:
                process_domain_offers_otodom(driver, website_arguments, timestamp)
                pass
            else:
                raise RequestException(f"Unrecognized URL: {url}")

    except Exception as e:
        if LOGGING["debug"]:
            raise e

        logging.error("Error occurred: %s", e)
