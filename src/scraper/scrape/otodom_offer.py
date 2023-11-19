from _utils import get_text_by_selector, wait_for_conditions, presence_of_element
from bs4 import BeautifulSoup


def get_offer_from_otodom(offer_url: str, driver) -> dict:
    field_selectors = {
        "main_points": '[data-testid="ad.top-information.table"]',
        "additional_points": '[data-testid="ad.additional-information.table"]',
        "title": '[data-cy="adPageAdTitle"]',
        "location": 'data-testid="map-link-container"',
        "price": '[data-cy="adPageHeaderPrice"]',
        "square_meters": '[data-testid="table-value-area"]',
        "rent": '[data-testid="table-value-rent"]',
        "number_of_rooms": '[data-testid="table-value-rooms_num"]',
        "deposit": '[data-testid="table-value-deposit"]',
        "floor_level": '[data-testid="table-value-floor"]',
        "building_type": '[data-testid="table-value-building_type"]',
        "available_from": '[data-testid="table-value-free_from"]',
        "balcony_garden_terrace": '[data-testid="table-value-outdoor"]',
        "remote service": '[aria-label="Obsługa zdalna"]',
        "completion": '[data-testid="table-value-construction_status"]',
        "summary_description": '[data-testid="content-container"]',
        "ownership": '[data-testid="table-value-advertiser_type"]',
        "rent_to_students": '[data-testid="table-value-rent_to_students"]',
        "equipment": '[data-testid="table-value-equipment_types"]',
        "media_types": '[data-testid="table-value-media_types"]',
        "heating": '[data-testid="table-value-heating"]',
        "security": '[data-testid="table-value-security_types"]',
        "windows": '[data-testid="table-value-windows_type"]',
        "elevator": '[data-testid="table-value-lift"]',
        "parking_space": '[data-testid="table-value-car"]',
        "build_year": '[data-testid="table-value-build_year"]',
        "building_material": '[data-testid="table-value-building_material"]',
        "additional_information": '[data-testid="table-value-extras_types"]',
    }

    conditions_selectors = [
        {
            key: field_selectors[key]
            for key in [
                "main_points",
                "additional_points",
                "title",
                "location",
                "price",
                "summary_description",
            ]
        }
    ]

    if not wait_for_conditions(driver, *conditions_selectors):
        return None

    return "Passed"
    soup_offer = BeautifulSoup(driver.page_source, "html.parser")

    main_points = get_text_by_selector(
        offer_url, '[data-testid="ad.top-information.table"]'
    )

    additional_points = soup_offer.select_one(
        '[data-testid="ad.additional-information.table"]'
    )

    record = {
        "link": offer_url,
        "title": get_text_by_selector(soup_offer, '[data-cy="adPageAdTitle"'),
        "location": get_text_by_selector(
            soup_offer, 'data-testid="map-link-container"'
        ),
        "price": get_text_by_selector(soup_offer, '[data-cy="adPageHeaderPrice"]'),
        "square_meters": get_text_by_selector(
            main_points, '[data-testid="table-value-area"]'
        ),
        "rent": get_text_by_selector(main_points, '[data-testid="table-value-rent"'),
        "number_of_rooms": get_text_by_selector(
            main_points, '[data-testid="table-value-rooms_num"]'
        ),
        "deposit": get_text_by_selector(
            main_points, '[data-testid="table-value-deposit"]'
        ),
        "floor_level": get_text_by_selector(
            main_points, '[data-testid="table-value-floor"]'
        ),
        "building_type": get_text_by_selector(
            main_points, '[data-testid="table-value-building_type"]'
        ),
        "available_from": get_text_by_selector(
            main_points, '[data-testid="table-value-free_from"]'
        ),
        "balcony_garden_terrace": get_text_by_selector(
            main_points, '[data-testid="table-value-outdoor"]'
        ),
        "remote service": get_text_by_selector(
            main_points,
            # the test-id is not provided
            '[aria-label="Obsługa zdalna"]',
        ),
        "completion": get_text_by_selector(
            main_points, '[data-testid="table-value-construction_status"]'
        ),
        "summary_description": get_text_by_selector(
            soup_offer, '[data-testid="content-container"]'
        ),
        "ownership": get_text_by_selector(
            additional_points, '[data-testid="table-value-advertiser_type"]'
        ),
        "rent_to_students": get_text_by_selector(
            additional_points, '[data-testid="table-value-rent_to_students"]'
        ),
        "equipment": get_text_by_selector(
            additional_points, '[data-testid="table-value-equipment_types"]'
        ),
        "media_types": get_text_by_selector(
            additional_points, '[data-testid="table-value-media_types"]'
        ),
        "heating": get_text_by_selector(
            additional_points, '[data-testid="table-value-heating"]'
        ),
        "security": get_text_by_selector(
            additional_points, '[data-testid="table-value-security_types"]'
        ),
        "windows": get_text_by_selector(
            additional_points, '[data-testid="table-value-windows_type"]'
        ),
        "elevator": get_text_by_selector(
            additional_points, '[data-testid="table-value-lift"]'
        ),
        "parking_space": get_text_by_selector(
            additional_points, '[data-testid="table-value-car"]'
        ),
        "build_year": get_text_by_selector(
            additional_points, '[data-testid="table-value-build_year"]'
        ),
        "building_material": get_text_by_selector(
            additional_points, '[data-testid="table-value-building_material"]'
        ),
        "additional_information": get_text_by_selector(
            additional_points, '[data-testid="table-value-extras_types"]'
        ),
    }

    return record
