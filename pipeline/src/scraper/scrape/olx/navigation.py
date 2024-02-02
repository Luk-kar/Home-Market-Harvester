# Third-party imports
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Local imports
from pipeline.src.scraper.config import SCRAPER


def return_to_listing_page(driver: WebDriver):
    """
    Closes the current window and switches back to the main listing page.

    Args:
        driver (WebDriver): The WebDriver instance.

    Returns:
        None
    """
    driver.close()
    driver.switch_to.window(driver.window_handles[0])


def open_new_offer(driver: WebDriver, offer_url: str):
    """
    Opens a new offer in a new tab/window using the provided WebDriver instance.

    Args:
        driver (WebDriver): The WebDriver instance to use for opening the offer.
        offer_url (str): The URL of the offer to open.

    Returns:
        None
    """
    driver.execute_script(f"window.open('{offer_url}', '_blank');")
    driver.switch_to.window(driver.window_handles[1])


def click_next_page(driver: WebDriver, selector: str):
    """
    Click the next page button.

    Args:
        driver (WebDriver): The WebDriver instance for interacting with the browser.
        selector (str): The CSS selector for identifying the next page button.

    Returns:
        None
    """

    wait = WebDriverWait(driver, SCRAPER["wait_timeout"])
    next_page_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
    )

    try:
        scroll_into_element = "arguments[0].scrollIntoView();"
        driver.execute_script(scroll_into_element, next_page_button)

        next_page_button.click()

    except Exception:
        javascript_click = "arguments[0].click();"
        driver.execute_script(javascript_click, next_page_button)
