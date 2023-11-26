# Standard imports
import datetime
import re

# Third-party imports
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Local imports
from _utils import humans_delay, save_to_csv
from config import SUBDOMAINS
from scrape.otodom.process_offer import process_offer as process_offer_otodom


def process_page_offers(
    driver: WebDriver, website_arguments: dict, timestamp: str, offers_count: int = 0
):
    location_query = website_arguments["location_query"]
    offers_cap = website_arguments["scraped_offers_cap"]
    soup = BeautifulSoup(driver.page_source, "html.parser")

    listing_links = soup.find_all("a", {"data-cy": "listing-item-link"})

    original_window = driver.current_window_handle

    for sub_link in listing_links:
        if offers_count >= offers_cap:
            break

        open_process_and_close_window(
            driver, original_window, sub_link, location_query, timestamp
        )

        offers_count += 1

    return offers_count


def open_process_and_close_window(
    driver, original_window, sub_link, location_query: str, timestamp: str
):
    open_offer(driver, sub_link)

    humans_delay(1, 2)

    record = process_offer_otodom(driver)

    if record:
        save_to_csv(record, location_query, SUBDOMAINS["otodom"], timestamp)

    driver.close()

    driver.switch_to.window(original_window)


def open_offer(driver, query_string):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    full_link = SUBDOMAINS["otodom"] + query_string["href"]
    driver.get(full_link)


def process_domain_offers_otodom(
    driver: WebDriver, website_arguments, timestamp: str, offers_count: int
):
    location = website_arguments["location_query"]
    km = website_arguments["area_radius"]
    offers_cap = website_arguments["scraped_offers_cap"]

    display_offers(driver, location, km)

    humans_delay(0.3, 0.5)

    set_max_offers_per_site(driver)

    humans_delay(0.2, 0.4)

    await_for_offers_to_load(driver)

    # process for the first time
    offers_count += process_page_offers(
        driver, website_arguments, timestamp, offers_count
    )

    if offers_count >= offers_cap:
        return offers_count

    next_page_selector = '[data-cy="pagination.next-page"]'

    while not is_disabled(driver, next_page_selector):
        await_for_offers_to_load(driver)
        humans_delay(0.3, 0.5)

        offers_count += process_page_offers(
            driver, website_arguments, timestamp, offers_count
        )

        if offers_count >= offers_cap:
            return offers_count

        click_next_page(driver)

    return offers_count


def is_disabled(driver, selector):
    try:
        selector = f'{selector}[disabled=""]'

        driver.find_element(By.CSS_SELECTOR, selector)
        return True
    except NoSuchElementException:
        return False


def click_next_page(driver):
    next_button_selector = '[data-cy="pagination.next-page"]'
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, next_button_selector))
    )
    next_button = driver.find_element(By.CSS_SELECTOR, next_button_selector)
    next_button.click()


def await_for_offers_to_load(driver):
    main_feed_selector = '[role="main"]'
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, main_feed_selector))
    )


def set_max_offers_per_site(driver):
    entries_id = "react-select-entriesPerPage-input"
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, entries_id)))
    entries_per_page = driver.find_element(By.ID, entries_id)
    entries_per_page.click()

    entries_per_page_id = "react-select-entriesPerPage-listbox"
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, entries_per_page_id))
    )
    entries_per_page_listbox = driver.find_element(By.ID, entries_per_page_id)

    last_option_selector = ".react-select__menu-list > .react-select__option:last-child"
    last_option_element = entries_per_page_listbox.find_element(
        By.CSS_SELECTOR, last_option_selector
    )
    last_option_element.click()


def display_offers(driver, text_to_enter, km):
    field_selectors = {
        "cookies_banner": '[id="onetrust-banner-sdk"]',
        "accept_cookies": '[id="onetrust-accept-btn-handler"]',
        "user_form": '[data-testid="form-wrapper"]',
        "transaction_type": '[data-cy="search-form--field--transaction"]',
        "for_rent": "#react-select-transaction-option-0",
        "location": '[data-testid="search.form.location.button"]',
        "location_input": "location-picker-input",
        "location_dropdown": '[data-testid="search.form.location.container"]',
        "location_suggestions": 'li[data-testid="suggestions-item"]',
        "distance_radius": '[data-cy="search-form--field--distanceRadius"]',
        "distance_radius_dropdown": 'div[data-cy="search.form.location.dropdown.list-wrapper"]',
        "distance_radius_options": "react-select-distanceRadius-listbox",
        "distance_radius_suggestions": "li[data-testid='suggestions-item']",
    }

    accept_cookies(driver, field_selectors)

    humans_delay(0.15, 0.2)

    select_for_rent_option(driver, field_selectors)

    humans_delay(0.15, 0.4)

    select_distance_radius(driver, field_selectors, km)

    humans_delay(0.3, 0.5)

    write_location(driver, field_selectors, text_to_enter)

    humans_delay(0.3, 0.5)

    press_find_offers_button(driver)


def press_find_offers_button(driver):
    ActionChains(driver).send_keys(Keys.ENTER).perform()


def write_location(driver, field_selectors, text_to_enter):
    location_element = driver.find_element(By.CSS_SELECTOR, field_selectors["location"])
    location_element.click()

    humans_delay(0.2, 0.4)

    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.ID, field_selectors["location_input"]))
    )
    input_element = driver.find_element(By.ID, field_selectors["location_input"])
    input_element.send_keys(text_to_enter)

    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, field_selectors["location_dropdown"])
        )  # todo
    )
    location_dropdown = driver.find_element(
        By.CSS_SELECTOR, field_selectors["location_dropdown"]
    )
    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, field_selectors["location_suggestions"])
        )
    )
    suggestions = location_dropdown.find_elements(
        By.CSS_SELECTOR, field_selectors["location_suggestions"]
    )

    closest_match = suggestions[0]
    closest_match.click()


def select_distance_radius(driver, field_selectors, km):
    distance_dropdown = {
        # Km : index
        0: 0,
        5: 1,
        10: 2,
        15: 3,
        25: 4,
        50: 5,
        75: 6,
    }

    select_option = distance_dropdown[km]

    distance_radius_element = driver.find_element(
        By.CSS_SELECTOR, field_selectors["distance_radius"]
    )
    distance_radius_element.click()
    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located(
            (By.ID, field_selectors["distance_radius_options"])
        )
    )

    distance_radius_options_element = driver.find_element(
        By.ID, field_selectors["distance_radius_options"]
    )

    div_elements = distance_radius_options_element.find_elements(By.TAG_NAME, "div")

    # Regular expression pattern to match the IDs
    pattern = re.compile("react-select-distanceRadius-option-\d+")

    # Filter elements based on the pattern
    matching_elements = [
        element
        for element in div_elements
        if pattern.match(element.get_attribute("id"))
    ]

    matching_elements[select_option].click()


def select_for_rent_option(driver, field_selectors):
    user_form = driver.find_element(
        By.CSS_SELECTOR,
        field_selectors["user_form"],
    )
    transaction_type = user_form.find_element(
        By.CSS_SELECTOR,
        field_selectors["transaction_type"],
    )
    transaction_type.click()

    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, field_selectors["for_rent"]))
    )
    transaction_type.find_element(By.CSS_SELECTOR, field_selectors["for_rent"]).click()


def accept_cookies(driver, field_selectors):
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, field_selectors["cookies_banner"])
        )
    )
    accept_cookies_button = driver.find_element(
        By.CSS_SELECTOR,
        f"{field_selectors['cookies_banner']} {field_selectors['accept_cookies']}",
    )
    humans_delay(0.2, 0.4)
    accept_cookies_button.click()

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, field_selectors["user_form"]))
    )
