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
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    full_link = DOMAINS["otodom"] + offer_element["href"]
    driver.get(full_link)
