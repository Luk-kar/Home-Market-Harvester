"""
This module contains the core functionality 
for scraping real estate offers from multiple domains 
using Selenium WebDriver. 
It supports dynamic search criteria and manages the scraping process 
across different websites (such as OLX and Otodom), 
handling URL navigation, data extraction, and error handling. 
The module uses Enlighten for progress tracking and handles exceptions 
to ensure robust scraping even in case of connection issues 
or other unexpected errors.
"""

# Standard imports
import logging
import datetime

# Third-party imports
from requests.exceptions import RequestException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException
import enlighten


# Local imports
from pipeline.src.a_scraping._utils.selenium_utils import humans_delay
from pipeline.src.a_scraping._utils.string_transformations import (
    transform_location_to_url_format,
)
from pipeline.src.a_scraping.config import DOMAINS, LOGGING
from pipeline.src.a_scraping.scrape.olx.process_olx_site_offers import (
    process_domain_offers_olx,
)
from pipeline.src.a_scraping.scrape.otodom.otodom_main_page import (
    process_domain_offers_otodom,
)


def scrape_offers(driver: WebDriver, search_criteria: dict):
    """
    Scrapes offers from different websites based on the provided search criteria.

    Args:
        driver (WebDriver): The web driver used to navigate the websites.
        search_criteria (dict): The search criteria containing location query and
        scraped offers cap.

    Raises:
        RequestException: If an unrecognized URL is encountered.

    Returns:
        None
    """
    try:
        location_query = search_criteria["location_query"]
        offers_cap = search_criteria["scraped_offers_cap"]

        progress = enlighten.Counter(
            desc="Scraping Offers",
            unit="offers",
            color="green",
            total=offers_cap,
        )

        formatted_location = transform_location_to_url_format(location_query)
        urls = [
            f'{DOMAINS["olx"]["domain"]}/{DOMAINS["olx"]["category"]}q-{formatted_location}/',
            DOMAINS["otodom"],
        ]
        timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        scraped_urls: set[str] = set()

        for url in urls:
            if progress.count >= offers_cap:
                break

            humans_delay()
            try:
                driver.get(url)
            except WebDriverException as error:
                # Attempt to refresh the page or handle the error as needed
                if LOGGING["debug"]:
                    raise error

                logging.error("Connection issue encountered: %s", error)
                driver.refresh()

            if DOMAINS["olx"]["domain"] in url:
                process_domain_offers_olx(
                    driver, search_criteria, timestamp, progress, scraped_urls
                )
            elif DOMAINS["otodom"] in url:
                process_domain_offers_otodom(
                    driver, search_criteria, timestamp, progress, scraped_urls
                )
            else:
                raise RequestException(f"Unrecognized URL: {url}")

    except Exception as error:
        if LOGGING["debug"]:
            raise error

        logging.error("Error occurred: %s", error)
