from _utils import get_text_by_selector, wait_for_conditions, presence_of_element
from bs4 import BeautifulSoup


def get_offer_from_otodom(offer_url: str, driver) -> dict:
    conditions = [
        presence_of_element('[data-testid="ad.top-information.table"]'),
        presence_of_element('[data-testid="ad.additional-information.table"]'),
        presence_of_element('[data-cy="adPageAdTitle"'),
        presence_of_element('data-testid="map-link-container"'),
        presence_of_element('[data-cy="adPageHeaderPrice"]'),
        presence_of_element('[data-testid="content-container"]'),
    ]

    if not wait_for_conditions(driver, *conditions):
        return None

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
