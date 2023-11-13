import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import pandas as pd
import os

# import time
import logging

# from datetime import datetime
from fake_useragent import UserAgent


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


# Function to handle the scraping logic
def scrape_olx(url):
    headers = {"User-Agent": UserAgent().random}
    try:
        response = requests.get(url, headers=headers)
        # will throw an error if the HTTP request returned an unsuccessful status code
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
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

            response_offer = requests.get(offer_url, headers=headers)
            response_offer.raise_for_status()
            soup_offer = BeautifulSoup(response_offer.content, "html.parser")

            if subdomain["olx"] in offer_url:
                description = soup_offer.select_one('[data-testid="main"]')

                listing_details = description.find("ul", class_="css-sfcl1s").find_all(
                    "li"
                )

                location_paragraphs = soup_offer.find(
                    "img", src="/app/static/media/staticmap.65e20ad98.svg"
                )

                record = {
                    "link": offer_url,
                    "date": safe_get_text(
                        description.select_one('[data-cy="ad-posted-at"]')
                    ),
                    "location": location_paragraphs,
                    "title": safe_get_text(
                        description.select_one('[data-cy="ad_title"]')
                    ),
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

                data = record

            elif subdomain["otodom"] in offer_url:
                main_points = offer_url.select_one(
                    '[data-testid="ad.top-information.table"]'
                )

                additional_points = offer_url.select_one(
                    '[data-testid="ad.additional-information.table"]'
                )

                record = {
                    "link": offer_url,
                    "title": safe_get_text(
                        offer_url.select_one('[data-cy="adPageAdTitle"')
                    ),
                    "loaction": safe_get_text(
                        offer_url.select_one('data-testid="map-link-container"')
                    ),
                    "price": safe_get_text(
                        offer_url.select_one('[data-cy="adPageHeaderPrice"]')
                    ),
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
                        main_points.select_one(
                            '[data-testid="table-value-building_type"]'
                        )
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
                        main_points.select_one(
                            '[data-testid="table-value-construction_status"]'
                        )
                    ),
                    "summary_description": safe_get_text(
                        offer_url.select_one('[data-testid="content-container"]')
                    ),
                    "ownership": safe_get_text(
                        additional_points.select_one(
                            '[data-testid="table-value-advertiser_type"]'
                        )
                    ),
                    "rent_to_students": safe_get_text(
                        additional_points.select_one(
                            '[data-testid="table-value-rent_to_students"]'
                        )
                    ),
                    "equipment": safe_get_text(
                        additional_points.select_one(
                            '[data-testid="table-value-equipment_types"]'
                        )
                    ),
                    "media_types": safe_get_text(
                        additional_points.select_one(
                            '[data-testid="table-value-media_types"]'
                        )
                    ),
                    "heating": safe_get_text(
                        additional_points.select_one(
                            '[data-testid="table-value-heating"]'
                        )
                    ),
                    "security": safe_get_text(
                        additional_points.select_one(
                            '[data-testid="table-value-security_types"]'
                        )
                    ),
                    "windows": safe_get_text(
                        additional_points.select_one(
                            '[data-testid="table-value-windows_type"]'
                        )
                    ),
                    "elevator": safe_get_text(
                        additional_points.select_one('[data-testid="table-value-lift"]')
                    ),
                    "parking_space": safe_get_text(
                        additional_points.select_one('[data-testid="table-value-car"]')
                    ),
                    "build_year": safe_get_text(
                        additional_points.select_one(
                            '[data-testid="table-value-build_year"]'
                        )
                    ),
                    "building_material": safe_get_text(
                        additional_points.select_one(
                            '[data-testid="table-value-building_material"]'
                        )
                    ),
                    "additional_information": safe_get_text(
                        additional_points.select_one(
                            '[data-testid="table-value-extras_types"]'
                        )
                    ),
                }

                data = record

            else:
                raise RequestException(f"Unrecognized URL: {offer_url}")

            break
        return data

    except requests.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        logging.error(f"Other error occurred: {err}")


# Function to save data to CSV
def save_to_csv(data, filename="data.csv"):
    df = pd.DataFrame([data])
    df.to_csv(filename, mode="a", index=False, header=not pd.read_csv(filename).empty)


# Main function to control the scraping process
def main():
    log_setup()

    # URL to scrape - replace with the specific URL you are interested in
    url = f'{search["domain"]}/{search["category"]}q-{search["location"]}/'
    # Scrape the data
    data = scrape_olx(url)
    print(data)
    # Save to CSV
    # save_to_csv(data)
    # Wait a bit before the next request
    # time.sleep(1)  # Sleep for 1 second


if __name__ == "__main__":
    # Run the main function
    main()
