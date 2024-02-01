"""
This module orchestrates the scraping process for real estate offers,
 managing web driver setup, data scraping, and file storage.
"""

# Standard imports
from typing import Optional, Dict
import argparse
import datetime
import os
import sys

# Local imports
from scraper.config import DATA
from scraper.logging_setup import log_setup
from scraper.scrape.process_sites_offers import scrape_offers
from scraper.webdriver_setup import get_driver

VALID_AREA_RADIUS = {0, 5, 10, 15, 25, 50, 75}


def parse_arguments():
    """Parses command line arguments for scraper settings."""
    parser = argparse.ArgumentParser(
        description="Run the web scraper for real estate offers."
    )
    parser.add_argument(
        "location_query",
        type=str,
        nargs="?",
        help="Location query for scraping. E.g. 'Warszawa'",
    )
    parser.add_argument(
        "area_radius",
        type=int,
        choices=VALID_AREA_RADIUS,
        nargs="?",
        help="Radius of the area for scraping in kilometers.",
    )
    parser.add_argument(
        "scraped_offers_cap",
        type=int,
        nargs="?",
        help="Maximum number of offers to scrape. E.g., 1, 10, 100, 500...",
    )
    return parser.parse_args()


def validate_arguments(location_query: str, area_radius: int, scraped_offers_cap: int):
    """Validates the provided command line arguments."""
    errors = []

    if not isinstance(location_query, str):
        errors.append("Location query must be a string.")

    if area_radius not in VALID_AREA_RADIUS:
        errors.append(f"Area radius must be one of {sorted(VALID_AREA_RADIUS)}.")

    if not isinstance(scraped_offers_cap, int):
        errors.append("Scraped offers cap must be a positive integer.")
    elif scraped_offers_cap <= 0:
        errors.append("Scraped offers cap must be a positive integer.")

    if errors:
        for error in errors:
            print(f"Error: {error}")
        sys.exit(1)


def main(
    location_query: Optional[str] = None,
    area_radius: Optional[float] = None,
    scraped_offers_cap: Optional[int] = None,
):
    """
    The main execution function of the scraper script.

    Args:
        location_query (str, optional): The location query for scraping. Defaults to None.
        area_radius (float, optional): The radius of the area for scraping in kilometers. Defaults to None.
        scraped_offers_cap (int, optional): The maximum number of offers to scrape. Defaults to None.
    """

    validate_arguments(location_query, area_radius, scraped_offers_cap)
    log_setup()
    driver = get_driver()

    search_criteria = {
        "location_query": location_query,
        "area_radius": area_radius,
        "scraped_offers_cap": scraped_offers_cap,
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
    args = parse_arguments()
    main(args.location_query, args.area_radius, args.scraped_offers_cap)
