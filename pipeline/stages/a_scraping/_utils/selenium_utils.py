"""
This module provides a collection of utility functions 
to assist with web scraping using Selenium and BeautifulSoup. 
"""

# Standard imports
from typing import Dict, List, Optional
import logging
import random
import time

# Third-party imports
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Local imports
from pipeline.config.a_scraping import SCRAPER


def await_element(
    driver,
    selector,
    by: str = By.CSS_SELECTOR,
    timeout: int | float = SCRAPER["wait_timeout"],
):
    """
    Waits for an element to be present in the DOM using the given selector.

    Args:
        driver (WebDriver): The WebDriver instance.
        selector (str): A dictionary containing the CSS selector for the element.
        by (str): The type of selector to use.
        timeout (int | float): The maximum time to wait for the element to be present.

    Returns:
        None
    """
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, selector)))


def humans_delay(
    min_seconds: float = SCRAPER["min_delay"], max_seconds: float = SCRAPER["max_delay"]
):
    """
    Pauses execution for a random period between `min_seconds` and `max_seconds`.

    Args:
    - min_seconds (float): The min of seconds to delay.
    - max_seconds (float): The max of seconds to delay.
    """
    time.sleep(random.uniform(min_seconds, max_seconds))


def safe_get_text(
    element: Optional[WebElement], default: Optional[str] = None
) -> Optional[str]:
    """
    Extracts text content from a web element safely.

    Args:
    - element (Optional[WebElement]): The WebElement from which to extract text.
    - default (Optional[str]): The default value to return if text extraction fails.

    Returns:
    - Optional[str]: The extracted text or the default value if extraction fails.
    """

    try:
        return element.text.strip() if element else default
    except AttributeError:
        return default


def wait_for_conditions(
    driver: WebDriver,
    *conditions,
    timeout: int = SCRAPER["multi_wait_timeout"],
    max_retries: int = SCRAPER["max_retries"],
) -> bool:
    """
    Waits for multiple conditions to be met within a specified timeout.

    Args:
    - driver (WebDriver): The WebDriver instance used to drive the browser.
    - *conditions: Variable length argument list of expected conditions.
    - timeout (int): Maximum time to wait for the conditions to be met.
    - max_retries (int): Maximum number of retries for each condition.

    Returns:
    - bool: True if all conditions are met within the timeout, False otherwise.
    """

    for condition in conditions:
        retry_count = 0
        while retry_count < max_retries:
            try:
                required_web_element = presence_of_element(condition)
                WebDriverWait(driver, timeout).until(required_web_element)
                break  # Condition met, exit retry loop
            except TimeoutException:
                retry_count += 1
                logging.warning(
                    "Condition not met, retrying... Attempt: %s", retry_count
                )
                if retry_count == max_retries:
                    return False
                driver.refresh()
    return True


def get_text_by_selector(
    soup: BeautifulSoup, selector: str, default: Optional[str] = None
) -> Optional[str]:
    """
    Extracts text content from a BeautifulSoup object using a CSS selector.

    Args:
    - soup (BeautifulSoup): The BeautifulSoup object to search within.
    - selector (str): The CSS selector to use for extracting text.
    - default (Optional[str]): The default value to return if no element is found.

    Returns:
    - Optional[str]: The extracted text or the default value if no element is found.
    """

    return safe_get_text(soup.select_one(selector), default)


def presence_of_element(selector: str):
    """
    Creates a condition that checks if an element is present on the DOM of a page.

    Args:
    - selector (str): The CSS selector to use for locating the element.

    Returns:
    - Callable: An expected condition that locates elements by CSS selector.
    """

    return EC.presence_of_element_located((By.CSS_SELECTOR, selector))


def extract_data(
    field_selectors: Dict[str, str],
    fields_to_extract: List[str],
    source_element,
    record: Dict[str, str],
):
    """
    Extracts data from the given source element based on the provided field selectors
    and updates the record dictionary with extracted values.

    Args:
    - field_selectors (Dict[str, str]): A dictionary mapping field names to CSS selectors.
    - fields_to_extract (List[str]): A list of field names that need to be extracted.
    - source_element: The source from which to extract the data,
    can be a BeautifulSoup object or WebElement.
    - record (Dict[str, str]): The dictionary to update with extracted data.

    Returns:
    - None
    """
    record.update(
        {
            field: get_text_by_selector(source_element, field_selectors[field])
            for field in fields_to_extract
            if field in field_selectors
        }
    )
