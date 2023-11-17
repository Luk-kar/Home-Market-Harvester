from webdriver_setup import get_driver
from logging_setup import log_setup
from scrape.listing_page import scrape_offers
from config import SCRAPER


def main():
    log_setup()
    driver = get_driver()

    try:
        url = f'{SCRAPER["domain"]}/{SCRAPER["category"]}q-{SCRAPER["location"]}/'
        data = scrape_offers(url, driver)
        print(data)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
