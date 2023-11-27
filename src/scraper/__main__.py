# Standard imports
from logging_setup import log_setup
from webdriver_setup import get_driver
import datetime
import os

# Local imports
from config import DATA, SCRAPER
from scrape.process_sites_offers import scrape_offers


def main():
    """
    The main execution function of the scraper script.

    This function sets up the logging, initializes the web driver,
    constructs the scraping URL, initiates the scraping process, and
    save the scraped data into CSV files (for each of the domains:
    "otodom" and "olx" separately).
    It ensures that the driver is properly
    closed after the scraping is done.
    """

    log_setup()
    driver = get_driver()

    search_criteria = {
        "location_query": SCRAPER["location_query"],
        "area_radius": SCRAPER["area_radius"],
        "scraped_offers_cap": SCRAPER["scraped_offers_cap"],
    }

    print(f"Start scraping at: {print_current_time()}\n")

    existing_folders = set(os.listdir(DATA["folder_scraped_data"]))

    try:
        scrape_offers(driver, search_criteria)

    finally:
        driver.quit()
        print(f"\nEnd scraping at:   {print_current_time()}")

        print_new_data_files(existing_folders)


def print_new_data_files(existing_folders: set):
    """
    Prints the new data files created in the folder.

    Args:
        existing_folders (set): A set of existing folders.

    Returns:
        None
    """
    folder_scraped_data = DATA["folder_scraped_data"]

    new_folders = set(os.listdir(folder_scraped_data)) - existing_folders

    print(f"\nNew files created in the folder {folder_scraped_data}\\:")

    for folder in new_folders:
        print(2 * " " + f"\\{folder}\\:")
        new_folder = f"{folder_scraped_data}\\{folder}"
        for new_file in os.listdir(new_folder):
            print(4 * " " + f"- {new_file}")


def print_current_time():
    """
    Prints the current date and time in the format "YYYY-MM-DD HH:MM:SS".
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    main()
