# Standard imports
from logging_setup import log_setup
from webdriver_setup import get_driver

# Local imports
from config import SCRAPER
from scrape.process_sites_offers import scrape_offers


def main():
    """
    The main execution function of the scraper script.

    This function sets up the logging, initializes the web driver,
    constructs the scraping URL, initiates the scraping process, and
    save the scraped data into CSV files (for each of the domains:
    "otodom" and "olx" separately).
    It ensures that the driver is properly
    closed after the scraping is done.
    """

    log_setup()
    driver = get_driver()

    try:
        website_arguments = {
            "location_query": SCRAPER["location_query"],
            "area_radius": SCRAPER["area_radius"],
            "scraped_offers_cap": SCRAPER["scraped_offers_cap"],
        }

        scrape_offers(driver, website_arguments)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
