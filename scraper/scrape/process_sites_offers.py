# Standard imports
import logging
import datetime

# Third-party imports
from requests.exceptions import RequestException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException
import enlighten


# Local imports
from scraper._utils.selenium_utils import humans_delay
from scraper._utils.string_transformations import transform_location_to_url_format
from scraper.config import DOMAINS, LOGGING
from scraper.scrape.olx.process_olx_site_offers import process_domain_offers_olx
from scraper.scrape.otodom.otodom_main_page import process_domain_offers_otodom


def scrape_offers(driver: WebDriver, search_criteria: dict):
    """
    Scrapes offers from different websites based on the provided search criteria.

    Args:
        driver (WebDriver): The web driver used to navigate the websites.
        search_criteria (dict): The search criteria containing location query and scraped offers cap.

    Raises:
        RequestException: If an unrecognized URL is encountered.

    Returns:
        None
    """
    try:
        location_query = search_criteria["location_query"]
        offers_cap = search_criteria["scraped_offers_cap"]

        progress = enlighten.Counter(
            desc="Total progress",
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
            except WebDriverException as e:
                # Attempt to refresh the page or handle the error as needed
                if LOGGING["debug"]:
                    raise e

                logging.error("Connection issue encountered: %s", e)
                driver.refresh()

            if DOMAINS["olx"]["domain"] in url:
                process_domain_offers_olx(
                    driver, search_criteria, timestamp, progress, scraped_urls
                )
            elif DOMAINS["otodom"] in url:
                process_domain_offers_otodom(
                    driver, search_criteria, timestamp, progress, scraped_urls
                )
                pass
            else:
                raise RequestException(f"Unrecognized URL: {url}")

    except Exception as e:
        if LOGGING["debug"]:
            raise e

        logging.error("Error occurred: %s", e)