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
import datetime
import logging
import random
import time

# Third-party imports
from requests.exceptions import RequestException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException
import enlighten


# Local imports
from pipeline.stages.a_scraping._utils.selenium_utils import humans_delay
from pipeline.stages.a_scraping._utils.string_transformations import (
    transform_location_to_url_format,
)
from pipeline.stages.a_scraping.config import DOMAINS, LOGGING
from pipeline.stages.a_scraping.scrape.olx.process_olx_site_offers import (
    process_domain_offers_olx,
)
from pipeline.stages.a_scraping.scrape.otodom.otodom_main_page import (
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
                driver = get_website(driver, url)
            except WebDriverException as error:
                logging.error("Error occurred: %s", error)
                continue

            if DOMAINS["olx"]["domain"] in url:

                try:
                    process_domain_offers_olx(
                        driver, search_criteria, timestamp, progress, scraped_urls
                    )
                except Exception as error:
                    logging.error(f"Error processing OLX offers: {error}")
                    raise error

            elif DOMAINS["otodom"] in url:

                try:
                    process_domain_offers_otodom(
                        driver, search_criteria, timestamp, progress, scraped_urls
                    )
                except Exception as error:
                    logging.error(f"Error processing Otodom offers: {error}")
                    raise error

            else:
                raise RequestException(f"Unrecognized URL: {url}")

    except Exception as error:
        if LOGGING["debug"]:
            raise error

        logging.error("Error occurred: %s", error)


def get_website(driver: WebDriver, url: str) -> WebDriver:
    """
    Get the website using the provided WebDriver.

    Args:
        driver (WebDriver): The WebDriver instance.
        url (str): The URL of the website to navigate to.

    Returns:
        WebDriver: The WebDriver instance after navigating to the website.
    """
    max_retries = random.randint(4, 5)
    retry_delay = random.uniform(4, 5)
    attempts = 0

    while attempts < max_retries:
        try:
            driver.get(url)
            break
        except WebDriverException as error:
            attempts += 1
            message = (
                "Connection issue encountered. Retrying..."
                f"Attempt {attempts} of {max_retries}."
            )
            print(message)
            logging.warning(message)
            time.sleep(retry_delay)
            driver.refresh()

            # Attempt to refresh the page or handle the error as needed
            if attempts == max_retries:
                raise error

    return driver
