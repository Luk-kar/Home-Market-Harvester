# Third-party imports
from enlighten import Counter
from selenium.webdriver.remote.webdriver import WebDriver

# Local imports
from _utils.selenium_utils import humans_delay
from _utils.csv_utils import save_to_csv
from config import DOMAINS, SCRAPER
from scrape.otodom.process_offer import process_offer as process_offer_otodom


def open_process_and_close_window(
    driver: WebDriver,
    original_window: str,
    offer_element: dict[str, str],
    location_query: str,
    timestamp: str,
    progress: Counter,
):
    """
    Opens the offer in a new window, processes the offer data, saves it to a CSV file,
    and closes the window.

    Args:
        driver (WebDriver): The WebDriver instance used for web scraping.
        original_window (str): The original previous window handle.
        offer_element (dict[str, str]): The offer element containing information about the offer.
        location_query (str): The location query used for scraping.
        timestamp (str): The timestamp of the scraping process.
        progress (Counter): The progress counter used to track the number of processed offers.

    Returns:
        None
    """
    open_offer(driver, offer_element)

    if SCRAPER["anti_anti_bot"]:
        humans_delay()

    record = process_offer_otodom(driver)

    if record:
        save_to_csv(record, location_query, DOMAINS["otodom"], timestamp)
        progress.update()

    driver.close()

    driver.switch_to.window(original_window)


def open_offer(driver: WebDriver, offer_element: dict[str, str]):
    """
    Opens the offer page in a new window/tab using the provided WebDriver instance.

    Args:
        driver (WebDriver): The WebDriver instance used to control the browser.
        offer_element (dict[str, str]): A dictionary containing information about the offer element.

    Returns:
        None
    """
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    full_link = DOMAINS["otodom"] + offer_element["href"]
    driver.get(full_link)
