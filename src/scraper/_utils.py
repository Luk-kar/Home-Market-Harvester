from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

# import time
import logging
import random
import time

from custom_exceptions import ConditionNotMetException


def random_delay(min_seconds=0.90, max_seconds=1.30):
    """
    Generates a random delay between min_seconds and max_seconds
    """
    time.sleep(random.uniform(min_seconds, max_seconds))


def safe_get_text(element, default=None):
    try:
        return element.text.strip() if element else default
    except AttributeError:
        return default


def element_with_attribute(driver, tag, attribute, value):
    elements = driver.find_elements(By.TAG_NAME, tag)
    return next(
        (element for element in elements if element.get_attribute(attribute) == value),
        None,
    )


def wait_for_conditions(driver, *conditions, timeout=5, max_retries=5):
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
                    raise ConditionNotMetException(
                        f"Condition failed {max_retries} times."
                    )
                driver.refresh()
    return True
