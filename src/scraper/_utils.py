from typing import Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from typing import Optional
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC

# import time
import logging
import random
import time
from config import SCRAPER


def random_delay(
    min_seconds: float = SCRAPER["min_delay"], max_seconds: float = SCRAPER["max_delay"]
):
    """
    Generates a random delay between min_seconds and max_seconds
    """
    time.sleep(random.uniform(min_seconds, max_seconds))


def safe_get_text(
    element: Optional[WebElement], default: Optional[str] = None
) -> Optional[str]:
    try:
        return element.text.strip() if element else default
    except AttributeError:
        return default


def element_with_attribute(driver: WebDriver, tag: str, attribute: str, value: str):
    elements = driver.find_elements(By.TAG_NAME, tag)
    return next(
        (element for element in elements if element.get_attribute(attribute) == value),
        None,
    )


def wait_for_conditions(
    driver: WebDriver,
    *conditions,
    timeout: int = SCRAPER["multi_wait_timeout"],
    max_retries: int = SCRAPER["max_retries"],
) -> bool:
    """
    Waits for all specified conditions to be met within a given timeout. Raises an
    exception if any condition is not met 5 times consecutively.
    """
    for condition in conditions:
        retry_count = 0
        while retry_count < max_retries:
            try:
                WebDriverWait(driver, timeout).until(condition)
                break  # Condition met, exit retry loop
            except TimeoutException:
                retry_count += 1
                logging.warning(
                    f"Condition not met, retrying... Attempt: {retry_count}"
                )
                if retry_count == max_retries:
                    return False
                driver.refresh()
    return True


def get_text_by_selector(
    soup: BeautifulSoup, selector: str, default: Optional[str] = None
) -> Optional[str]:
    return safe_get_text(soup.select_one(selector), default)


def presence_of_element(selector: str):
    return EC.presence_of_element_located((By.CSS_SELECTOR, selector))
