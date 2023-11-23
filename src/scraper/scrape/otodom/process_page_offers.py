# Standard imports
import re

# Third-party imports
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains


# Local imports
from _utils import random_delay


def process_page_offers(driver: WebDriver):
    field_selectors = {
        "cookies_banner": '[id="onetrust-banner-sdk"]',
        "accept_cookies": '[id="onetrust-accept-btn-handler"]',
        "user_form": '[data-testid="form-wrapper"]',
        "transaction_type": '[data-cy="search-form--field--transaction"]',
        "location": '[data-testid="search.form.location.button"]',
        "distance_radius": '[data-cy="search-form--field--distanceRadius"]',
    }

    # Accept cookies
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, field_selectors["cookies_banner"])
        )
    )
    accept_cookies_button = driver.find_element(
        By.CSS_SELECTOR,
        f"{field_selectors['cookies_banner']} {field_selectors['accept_cookies']}",
    )
    random_delay(0.2, 0.4)
    accept_cookies_button.click()

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, field_selectors["user_form"]))
    )

    # Select transaction type
    user_form = driver.find_element(
        By.CSS_SELECTOR,
        field_selectors["user_form"],
    )
    transaction_type = user_form.find_element(
        By.CSS_SELECTOR,
        field_selectors["transaction_type"],
    )
    # Click to open the dropdown
    transaction_type.click()

    fro_rent_option = "#react-select-transaction-option-0"
    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, fro_rent_option))
    )
    transaction_type.find_element(By.CSS_SELECTOR, fro_rent_option).click()
    random_delay(0.15, 0.4)

    # Select distance radius
    distance_radius_selector = field_selectors["distance_radius"]

    # Find the element and click on it
    distance_radius_element = driver.find_element(
        By.CSS_SELECTOR, distance_radius_selector
    )

    # Click to open the dropdown
    distance_radius_element.click()

    distance_radius_options = "react-select-distanceRadius-listbox"
    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.ID, distance_radius_options))
    )

    distance_radius_options_element = driver.find_element(
        By.ID, distance_radius_options
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

    random_delay(0.25, 0.45)

    # Select location
    location_selector = field_selectors["location"]

    # Find the element and click on it
    location_element = driver.find_element(By.CSS_SELECTOR, location_selector)
    location_element.click()

    random_delay(0.2, 0.4)

    location_input = "location-picker-input"
    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.ID, location_input))
    )
    input_element = driver.find_element(By.ID, location_input)
    text_to_enter = "Mierzęcice, Będziński, Śląskie"
    input_element.send_keys(text_to_enter)

    # Select the first option from the dropdown
    first_li_selector = "div[data-cy='search.form.location.dropdown.list-wrapper'] li[data-testid='suggestions-item']:first-child"

    # Wait for the element to be clickable
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, first_li_selector))
    )

    # Find the first li element and click on it
    first_li_element = driver.find_element(By.CSS_SELECTOR, first_li_selector)
    first_li_element.click()

    random_delay(0.3, 0.5)

    # await button with the result

    ActionChains(driver).send_keys(Keys.ENTER).perform()
    # todo

    # input_element.send_keys(Keys.ENTER)
    random_delay(400, 400)

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
