# Standard imports
import datetime
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

    search_criteria = {
        "location_query": SCRAPER["location_query"],
        "area_radius": SCRAPER["area_radius"],
        "scraped_offers_cap": SCRAPER["scraped_offers_cap"],
    }

    print(f"Start scraping at: {print_current_time()}\n")

    try:
        scrape_offers(driver, search_criteria)

    finally:
        driver.quit()
        print(f"\nEnd scraping at:   {print_current_time()}")


def print_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    main()
