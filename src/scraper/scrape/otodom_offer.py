from _utils import safe_get_text, wait_for_conditions
from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


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
