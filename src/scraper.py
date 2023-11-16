from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import pandas as pd
import os

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException

# import time
import logging
import random
import time

# from datetime import datetime
from fake_useragent import UserAgent


def random_delay(min_seconds=0.90, max_seconds=1.30):
    """
    Generates a random delay between min_seconds and max_seconds
    """
    time.sleep(random.uniform(min_seconds, max_seconds))


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")

    args = [f"user-agent={UserAgent().random}", "--headless"]

    for arg in args:
        options.add_argument(arg)

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()), options=options
    )

    return driver


def log_setup():
    if not os.path.exists("./logs"):
        os.makedirs("./logs")

    # Create a logger object
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Set the log level

    # Create handlers - one for file output, one for console output
    file_handler = logging.FileHandler("./logs/scraper.log")
    console_handler = logging.StreamHandler()

    # Create a logging format
    formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def safe_get_text(element, default=None):
    try:
        return element.text.strip() if element else default
    except AttributeError:
        return default


search = {
    "location": "Katowice",
    "domain": "https://www.olx.pl",
    "category": "nieruchomosci/mieszkania/wynajem/",
}


def element_with_attribute(driver, tag, attribute, value):
    elements = driver.find_elements(By.TAG_NAME, tag)
    return next(
        (element for element in elements if element.get_attribute(attribute) == value),
        None,
    )


# Function to handle the scraping logic
def scrape_olx(url, driver):
    try:
        try:
            driver.get(url)
        except WebDriverException as e:
            logging.error(f"Connection issue encountered: {e}")
            # Attempt to refresh the page or handle the error as needed
            driver.refresh()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[data-testid="listing-grid"]')
            )
        )

        soup = BeautifulSoup(driver.page_source, "html.parser")
        offers_listings = soup.select_one('[data-testid="listing-grid"]')

        offers = offers_listings.select('[data-testid="l-card"]')
        url_offers = []
        data = None

        for offer in offers:
            first_anchor_tag = offer.select_one("a")

            if first_anchor_tag:
                href_link = first_anchor_tag["href"]
                url_offers.append(href_link)
            else:
                offer_id = offer["id"] if "id" in offer.attrs else "Unknown"
                logging.info(f"No link found in the offer with id={offer_id}")

        for offer_url in url_offers:
            subdomain = {"olx": search["domain"], "otodom": "www.otodom.pl"}
            if not offer_url.startswith("http"):
                offer_url = search["domain"] + offer_url

            random_delay()  # Human behavior, anti-anti-bot

            driver.execute_script(f"window.open('{offer_url}', '_blank');")
            driver.switch_to.window(driver.window_handles[1])

            try:
                if subdomain["olx"] in offer_url:
                    data = get_offer_from_olx(offer_url, driver)

                elif subdomain["otodom"] in offer_url:
                    data = get_offer_from_otodom(offer_url, driver)

                else:
                    raise RequestException(f"Unrecognized URL: {offer_url}")

            except ConditionNotMetException as e:
                logging.error(f"Failed to process {offer_url}: {e}")

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            break

        return data

    except Exception as e:
        logging.error(f"Error occurred: {e}")


class ConditionNotMetException(Exception):
    """Exception raised when a condition is not met repeatedly."""

    pass


def wait_for_conditions(driver, *conditions, timeout=5, max_retries=5):
    """
    Waits for all specified conditions to be met within a given timeout. Raises an
    exception if any condition is not met 5 times consecutively.
    """
    for condition in conditions:
        retry_count = 0
        while retry_count < max_retries:
            try:
                WebDriverWait(driver, timeout).until(condition)
                break  # Condition met, exit retry loop
            except TimeoutException:
                retry_count += 1
                logging.warning(
                    f"Condition not met, retrying... Attempt: {retry_count}"
                )
                if retry_count == max_retries:
                    raise ConditionNotMetException(
                        f"Condition failed {max_retries} times."
                    )
                driver.refresh()
    return True


def get_offer_from_olx(offer_url, driver):
    wait_for_conditions(
        driver,
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="main"]')),
        lambda driver: element_with_attribute(
            driver, "img", "src", "/app/static/media/staticmap.65e20ad98.svg"
        )
        is not None,
    )

    soup_offer = BeautifulSoup(driver.page_source, "html.parser")

    description = soup_offer.select_one('[data-testid="main"]')

    listing_details = description.find("ul", class_="css-sfcl1s").find_all("li")

    location_paragraphs = soup_offer.find(
        "img", src="/app/static/media/staticmap.65e20ad98.svg"
    )

    record = {
        "link": offer_url,
        "date": safe_get_text(description.select_one('[data-cy="ad-posted-at"]')),
        "location": location_paragraphs.get("alt") if location_paragraphs else None,
        "title": safe_get_text(description.select_one('[data-cy="ad_title"]')),
        "price": safe_get_text(
            description.select_one('[data-testid="ad-price-container"]')
        ),
        "ownership": safe_get_text(listing_details[0]),
        "floor_level": safe_get_text(listing_details[1]),
        "is_furnished": safe_get_text(listing_details[2]),
        "building_type": safe_get_text(listing_details[3]),
        "square_meters": safe_get_text(listing_details[4]),
        "number_of_rooms": safe_get_text(listing_details[5]),
        "rent": safe_get_text(listing_details[6]),
        "summary_description": safe_get_text(
            description.select_one('[data-cy="ad_description"]')
        ),
    }

    return record


def get_offer_from_otodom(offer_url, driver):
    wait_for_conditions(
        driver,
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '[data-testid="ad.top-information.table"]')
        ),
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '[data-testid="ad.additional-information.table"]')
        ),
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="adPageAdTitle"')),
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'data-testid="map-link-container"')
        ),
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '[data-cy="adPageHeaderPrice"]')
        ),
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '[data-testid="content-container"]')
        ),
    )

    soup_offer = BeautifulSoup(driver.page_source, "html.parser")

    main_points = offer_url.select_one('[data-testid="ad.top-information.table"]')

    additional_points = soup_offer.select_one(
        '[data-testid="ad.additional-information.table"]'
    )

    record = {
        "link": offer_url,
        "title": safe_get_text(soup_offer.select_one('[data-cy="adPageAdTitle"')),
        "location": safe_get_text(
            soup_offer.select_one('data-testid="map-link-container"')
        ),
        "price": safe_get_text(soup_offer.select_one('[data-cy="adPageHeaderPrice"]')),
        "square_meters": safe_get_text(
            main_points.select_one('[data-testid="table-value-area"]')
        ),
        "rent": safe_get_text(
            main_points.select_one('[data-testid="table-value-rent"')
        ),
        "number_of_rooms": safe_get_text(
            main_points.select_one('[data-testid="table-value-rooms_num"]')
        ),
        "deposit": safe_get_text(
            main_points.select_one('[data-testid="table-value-deposit"]')
        ),
        "floor_level": safe_get_text(
            main_points.select_one('[data-testid="table-value-floor"]')
        ),
        "building_type": safe_get_text(
            main_points.select_one('[data-testid="table-value-building_type"]')
        ),
        "available_from": safe_get_text(
            main_points.select_one('[data-testid="table-value-free_from"]')
        ),
        "balcony_garden_terrace": safe_get_text(
            main_points.select_one('[data-testid="table-value-outdoor"]')
        ),
        "remote service": safe_get_text(
            main_points.select_one(
                # the test-id is not provided
                '[aria-label="Obsługa zdalna"]'
            )
        ),
        "completion": safe_get_text(
            main_points.select_one('[data-testid="table-value-construction_status"]')
        ),
        "summary_description": safe_get_text(
            soup_offer.select_one('[data-testid="content-container"]')
        ),
        "ownership": safe_get_text(
            additional_points.select_one('[data-testid="table-value-advertiser_type"]')
        ),
        "rent_to_students": safe_get_text(
            additional_points.select_one('[data-testid="table-value-rent_to_students"]')
        ),
        "equipment": safe_get_text(
            additional_points.select_one('[data-testid="table-value-equipment_types"]')
        ),
        "media_types": safe_get_text(
            additional_points.select_one('[data-testid="table-value-media_types"]')
        ),
        "heating": safe_get_text(
            additional_points.select_one('[data-testid="table-value-heating"]')
        ),
        "security": safe_get_text(
            additional_points.select_one('[data-testid="table-value-security_types"]')
        ),
        "windows": safe_get_text(
            additional_points.select_one('[data-testid="table-value-windows_type"]')
        ),
        "elevator": safe_get_text(
            additional_points.select_one('[data-testid="table-value-lift"]')
        ),
        "parking_space": safe_get_text(
            additional_points.select_one('[data-testid="table-value-car"]')
        ),
        "build_year": safe_get_text(
            additional_points.select_one('[data-testid="table-value-build_year"]')
        ),
        "building_material": safe_get_text(
            additional_points.select_one(
                '[data-testid="table-value-building_material"]'
            )
        ),
        "additional_information": safe_get_text(
            additional_points.select_one('[data-testid="table-value-extras_types"]')
        ),
    }

    data = record
    return data


def save_to_csv(data, filename="data.csv"):
    df = pd.DataFrame([data])
    df.to_csv(filename, mode="a", index=False, header=not pd.read_csv(filename).empty)


def main():
    log_setup()
    driver = get_driver()

    try:
        url = f'{search["domain"]}/{search["category"]}q-{search["location"]}/'
        data = scrape_olx(url, driver)
        print(data)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
