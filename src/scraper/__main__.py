# Standard imports
from logging_setup import log_setup
from webdriver_setup import get_driver

# Local imports
from scrape.process_site_offers import scrape_offers


def main():
    """
    The main execution function of the scraper script.

    This function sets up the logging, initializes the web driver,
    constructs the scraping URL, initiates the scraping process, and
    save the scraped data into CSV files (for each of the subdomains:
    "otodom" and "olx" separately).
    It ensures that the driver is properly
    closed after the scraping is done.
    """

    log_setup()
    driver = get_driver()

    try:
        # 0km, 5km, 10km, 15km, 25km, 50km, 75km
        km = 5
        location_query = "Mierzęcice, Będziński, Śląskie"

        scrape_offers(driver, location_query, km)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
