# Standard imports
from typing import Optional

# Third-party imports
from bs4 import BeautifulSoup
from selenium.webdriver.remote.webdriver import WebDriver

# Local imports
from _utils.selenium_utils import safe_get_text, wait_for_conditions, extract_data


def process_offer(driver: WebDriver) -> Optional[dict[str, str]]:
    field_selectors = {
        "description": '[data-testid="main"]',
        "location_paragraphs": 'img[src="/app/static/media/staticmap.65e20ad98.svg"]',
        "date": '[data-cy="ad-posted-at"]',
        "title": '[data-cy="ad_title"]',
        "price": '[data-testid="ad-price-container"]',
        "listing_details": "ul.css-sfcl1s > li",
        "summary_description": '[data-cy="ad_description"]',
    }

    conditions = [
        field_selectors[key] for key in ["description", "location_paragraphs"]
    ]

    if wait_for_conditions(driver, *conditions):
        return parse_offer_page(driver, field_selectors)
    else:
        return None


def parse_offer_page(driver: WebDriver, field_selectors: dict[str, str]):
    offer_url = driver.current_url

    soup_offer = BeautifulSoup(driver.page_source, "html.parser")
    description = soup_offer.select_one(field_selectors["description"])

    record = {}
    record["link"]: dict[str, str] = offer_url

    # Get header and description data
    extract_data(
        field_selectors,
        ["title", "location", "price", "summary_description"],
        description,
        record,
    )

    # Get location
    location_paragraphs = soup_offer.select_one(field_selectors["location_paragraphs"])
    record["location"] = location_paragraphs.get("alt") if location_paragraphs else None

    # Get listing details
    listing_details = description.select(field_selectors["listing_details"])
    detail_fields = [
        "ownership",
        "floor_level",
        "is_furnished",
        "building_type",
        "square_meters",
        "number_of_rooms",
        "rent",
    ]
    record.update(
        {
            field: safe_get_text(detail)
            for field, detail in zip(detail_fields, listing_details)
        }
    )

    return record
