from _utils import element_with_attribute, safe_get_text, wait_for_conditions
from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


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
