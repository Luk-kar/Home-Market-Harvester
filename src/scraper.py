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

            data = None

            if subdomain["olx"] in offer_url:
                description = soup_offer.select_one('[data-testid="main"]')

                listing_details = description.find("ul", class_="css-sfcl1s").find_all(
                    "li"
                )

                record = {
                    "link": offer_url,
                    "date": safe_get_text(
                        description.select_one('[data-cy="ad-posted-at"]')
                    ),
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
                    "ad_description": safe_get_text(
                        description.select_one('[data-cy="ad_description"]')
                    ),
                }

                data = record
                break

            elif subdomain["otodom"] in offer_url:
                pass
            else:
                raise RequestException(f"Unrecognized URL: {offer_url}")

        # Write the concatenated string to 'pages.txt'

        # Placeholder for data extraction logic
        # data = {
        #     'deal_id': '',
        #     'flat_id': '',
        #     'number_of_rooms': '',
        #     'is_furnished': '',
        #     'price': '',
        #     'deposit': '',
        #     'lease_time': '',
        # }
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
