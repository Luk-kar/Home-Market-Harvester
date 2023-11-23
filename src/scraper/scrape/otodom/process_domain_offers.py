# Standard imports
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
from _utils import humans_delay


def process_page_offers(driver: WebDriver):
    soup = BeautifulSoup(driver.page_source, "html.parser")

    listing_links = soup.find_all("a", {"data-cy": "listing-item-link"})

    original_window = driver.current_window_handle

    for link in listing_links:
        # Open a new window
        driver.execute_script("window.open('');")  # todo

        # Switch to the new window
        driver.switch_to.window(driver.window_handles[-1])

        # Navigate to the link
        driver.get(link)

        humans_delay(1, 2)
        # Close the new window
        driver.close()

        driver.switch_to.window(original_window)

    # for offer in offers:
    #     first_anchor_tag = offer.select_one("a")

    #     if first_anchor_tag:
    #         href_link = first_anchor_tag["href"]
    #         url_offers.append(href_link)
    #     else:
    #         offer_id = offer["id"] if "id" in offer.attrs else "Unknown"
    #         logging.info("No link found in the offer with id=%s", offer_id)

    # for offer_url in url_offers:
    #     subdomain = {"olx": SUBDOMAINS["olx"], "otodom": SUBDOMAINS["otodom"]}
    #     if not offer_url.startswith("http"):
    #         offer_url = subdomain["olx"] + offer_url

    #     if SCRAPER["anti-anti-bot"]:
    #         humans_delay()  # Human behavior

    #     driver.execute_script(f"window.open('{offer_url}', '_blank');")
    #     driver.switch_to.window(driver.window_handles[1])

    #     if subdomain["olx"] in offer_url:
    #         data = process_offer_olx(driver)

    #     elif subdomain["otodom"] in offer_url:
    #         data = process_offer_otodom(driver)

    #     else:
    #         raise RequestException(f"Unrecognized URL: {offer_url}")

    #     if data is None:
    #         if LOGGING["debug"]:
    #             raise OfferProcessingError(offer_url, "Failed to process offer URL")

    #         logging.error("Failed to process: %s", offer_url)

    #     driver.close()
    #     driver.switch_to.window(driver.window_handles[0])
    #     break  # todo


def process_domain_offers(driver: WebDriver):
    index = 0
    text_to_enter = "Mierzęcice, Będziński, Śląskie"

    display_offers(driver, text_to_enter, index)

    humans_delay(0.3, 0.5)

    set_max_offers_per_site(driver)

    humans_delay(0.3, 0.5)

    await_for_offers_to_load(driver)

    next_page_selector = '[data-cy="pagination.next-page"]'

    while not is_disabled(driver, next_page_selector):
        await_for_offers_to_load(driver)
        humans_delay(0.3, 0.5)

        process_page_offers(driver)

        humans_delay(400, 400)

        click_next_page(driver)

    humans_delay(400, 400)


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


def display_offers(driver, text_to_enter, index):
    field_selectors = {
        "cookies_banner": '[id="onetrust-banner-sdk"]',
        "accept_cookies": '[id="onetrust-accept-btn-handler"]',
        "user_form": '[data-testid="form-wrapper"]',
        "transaction_type": '[data-cy="search-form--field--transaction"]',
        "for_rent": "#react-select-transaction-option-0",
        "location": '[data-testid="search.form.location.button"]',
        "location_input": "location-picker-input",
        "distance_radius": '[data-cy="search-form--field--distanceRadius"]',
        "distance_radius_dropdown": 'div[data-cy="search.form.location.dropdown.list-wrapper"]',
        "distance_radius_options": "react-select-distanceRadius-listbox",
        "distance_radius_suggestions": "li[data-testid='suggestions-item']",
    }

    accept_cookies(driver, field_selectors)

    select_for_rent_option(driver, field_selectors)
    humans_delay(0.15, 0.4)

    select_distance_radius(driver, field_selectors)

    humans_delay(0.25, 0.45)

    write_location(driver, field_selectors, text_to_enter)

    # Select the first option from the dropdown

    choose_distance(driver, field_selectors, index)

    humans_delay(0.3, 0.5)

    press_find_offers_button(driver)


def press_find_offers_button(driver):
    ActionChains(driver).send_keys(Keys.ENTER).perform()


def choose_distance(driver, field_selectors, index):
    nth_child = index + 1
    first_li_selector = (
        f"{field_selectors['distance_radius_dropdown']} "
        f"{field_selectors['distance_radius_suggestions']}:nth-child({nth_child})"
    )
    # Wait for the element to be clickable
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, first_li_selector))
    )

    # Find the first li element and click on it
    first_li_element = driver.find_element(By.CSS_SELECTOR, first_li_selector)
    first_li_element.click()


def write_location(driver, field_selectors, text_to_enter):
    location_element = driver.find_element(By.CSS_SELECTOR, field_selectors["location"])
    location_element.click()

    humans_delay(0.2, 0.4)

    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.ID, field_selectors["location_input"]))
    )
    input_element = driver.find_element(By.ID, field_selectors["location_input"])
    input_element.send_keys(text_to_enter)


def select_distance_radius(driver, field_selectors):
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

    select_option = 2

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

    # soup = BeautifulSoup(driver.page_source, "html.parser")

    # offers_listings = soup.select_one('[data-testid="listing-grid"]')
    # offers = offers_listings.select('[data-testid="l-card"]')
    # url_offers = []

    # for offer in offers:
    #     first_anchor_tag = offer.select_one("a")

    #     if first_anchor_tag:
    #         href_link = first_anchor_tag["href"]
    #         url_offers.append(href_link)
    #     else:
    #         offer_id = offer["id"] if "id" in offer.attrs else "Unknown"
    #         logging.info("No link found in the offer with id=%s", offer_id)

    # for offer_url in url_offers:
    #     subdomain = {"olx": SUBDOMAINS["olx"], "otodom": SUBDOMAINS["otodom"]}
    #     if not offer_url.startswith("http"):
    #         offer_url = subdomain["olx"] + offer_url

    #     if SCRAPER["anti-anti-bot"]:
    #         random_delay()  # Human behavior

    #     driver.execute_script(f"window.open('{offer_url}', '_blank');")
    #     driver.switch_to.window(driver.window_handles[1])

    #     if subdomain["olx"] in offer_url:
    #         data = get_offer_from_olx(driver)

    #     elif subdomain["otodom"] in offer_url:
    #         data = get_offer_from_otodom(driver)

    #     else:
    #         raise RequestException(f"Unrecognized URL: {offer_url}")

    #     if data is None:
    #         if LOGGING["debug"]:
    #             raise OfferProcessingError(offer_url, "Failed to process offer URL")

    #         logging.error("Failed to process: %s", offer_url)

    #     driver.close()
    #     driver.switch_to.window(driver.window_handles[0])
    #     break  # todo

    # print(data)  # todo
