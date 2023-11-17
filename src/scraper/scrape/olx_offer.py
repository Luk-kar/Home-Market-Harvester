from _utils import safe_get_text, wait_for_conditions, extract_data
from bs4 import BeautifulSoup


def get_offer_from_olx(offer_url, driver):
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

    if not wait_for_conditions(driver, *conditions):
        return None

    soup_offer = BeautifulSoup(driver.page_source, "html.parser")
    description = soup_offer.select_one(field_selectors["description"])

    record = {}
    record["link"] = offer_url

    extract_data(
        field_selectors,
        ["title", "location", "price", "summary_description"],
        description,
        record,
    )

    location_paragraphs = soup_offer.select_one(field_selectors["location_paragraphs"])
    record["location"] = location_paragraphs.get("alt") if location_paragraphs else None

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
