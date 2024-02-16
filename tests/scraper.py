"""
Designed as a streamlined validation tool,
this test suite primarily ensures basic operational integrity
of the scraper in a live web environment.
"""

# Standard imports
from typing import Set
import csv
import datetime
import os
import shutil
import unittest

# Third-party imports
from bs4 import BeautifulSoup
from selenium.webdriver.remote.webdriver import WebDriver
import enlighten

# Local imports
from pipeline.stages.a_scraping._utils.selenium_utils import humans_delay
from pipeline.stages.a_scraping._utils.string_transformations import (
    transform_location_to_url_format,
)
from pipeline.stages.a_scraping.config import DATA, SCRAPER, DOMAINS
from pipeline.stages.a_scraping.scrape.olx.process_olx_site_offers import (
    process_domain_offers_olx,
)
from pipeline.stages.a_scraping.scrape.otodom.otodom_main_page import (
    process_domain_offers_otodom,
)
from pipeline.stages.a_scraping.webdriver_setup import get_driver
from pipeline.stages.a_scraping.__main__ import main


class TestScraper(unittest.TestCase):
    """A test suite for the scraper's core functionality."""

    # All catching exceptions should be generalized

    driver: WebDriver
    location_query: dict[str, str]
    search_criteria: dict[str, int | str | None]
    scraped_folder: str
    existing_folders_before: Set[str]
    new_folders: Set[str] | None

    def setUp(self) -> None:
        """Sets up test environment and initial conditions before each test."""

        self.driver = get_driver()
        self.location_query = {
            "low_volume": SCRAPER["location_query"],
            "high_volume": "Warszawa, mazowieckie",
        }
        self.search_criteria = {
            "location_query": None,
            "area_radius": 25,
            "scraped_offers_cap": 4,
        }
        self.scraped_folder = DATA["folder_scraped_data"]
        self.existing_folders_before = set(os.listdir(self.scraped_folder))
        self.new_folders = None

    def tearDown(self) -> None:
        """Cleans up after each test."""

        if self.new_folders is not None:
            for folder in self.new_folders:
                folder_path = os.path.join(self.scraped_folder, folder)
                shutil.rmtree(folder_path)

        self.driver.quit()

    def test_end_to_end(self) -> None:
        """Tests the end-to-end scraping functionality"""

        location_query = self.location_query["low_volume"]
        area_radius = 25
        scraped_offers_cap = 4

        try:
            main(location_query, area_radius, scraped_offers_cap)
        except Exception as error:
            self._dump_html("end_to_end_failure.html")
            self.fail(f"Scrape offers failed with {error}")

        self._verify_scraping_results()

    def test_olx_scrape_offers(self) -> None:
        """Tests scraping offers specifically from OLX."""

        try:
            self._setup_and_scrape_offers("high_volume", "olx")
        except Exception as error:
            self._dump_html("olx_scrape_failure.html")
            self.fail(f"Scrape offers failed with {error}")

        self._verify_scraping_results()

    def test_otodom_scrape_offers(self) -> None:
        """Tests scraping offers specifically from Otodom."""

        try:
            self._setup_and_scrape_offers("high_volume", "otodom")
        except Exception as erorr:
            self._dump_html("otodom_scrape_failure.html")
            self.fail(f"Scrape offers failed with {erorr}")

        self._verify_scraping_results()

    def _setup_and_scrape_offers(self, volume_type: str, domain: str) -> None:
        """Sets up and executes the scraping process for a given domain and volume type."""

        search_criteria = self.search_criteria.copy()
        search_criteria["location_query"] = self.location_query[volume_type]
        offers_cap = search_criteria["scraped_offers_cap"]

        progress = enlighten.Counter(
            desc="Total progress", unit="offers", color="green", total=offers_cap
        )

        timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        scraped_urls: set[str] = set()

        humans_delay()

        if domain == "olx":
            formatted_location = transform_location_to_url_format(
                search_criteria["location_query"]
            )
            url = f'{DOMAINS["olx"]["domain"]}/{DOMAINS["olx"]["category"]}q-{formatted_location}/'
            self.driver.get(url)
            process_domain_offers_olx(
                self.driver, search_criteria, timestamp, progress, scraped_urls
            )
        elif domain == "otodom":
            url = DOMAINS["otodom"]
            self.driver.get(url)
            process_domain_offers_otodom(
                self.driver, search_criteria, timestamp, progress, scraped_urls
            )

    def _verify_scraping_results(self) -> None:
        """Verifies the results of scraping by checking the generated folders and files."""

        existing_folders_after = set(os.listdir(self.scraped_folder))
        self.new_folders = existing_folders_after - self.existing_folders_before

        self.assertNotEqual(
            self.existing_folders_before,
            existing_folders_after,
            "No new data files were created.",
        )
        self.assertEqual(
            len(self.new_folders), 1, "There should be one folder for all created data."
        )

        self._check_csv_files()

    def _check_csv_files(self) -> None:
        """Checks if CSV files in new folders meet expected conditions."""

        for new_folder in self.new_folders:
            new_files = os.listdir(os.path.join(self.scraped_folder, new_folder))
            self.assertGreaterEqual(
                len(new_files), 1, f"Expected at least one file in {new_folder}."
            )
            for new_file in new_files:
                self.assertTrue(
                    new_file.endswith(".csv"), f"Expected a CSV file, got {new_file}."
                )

        counted_rows = 0
        for new_file in os.listdir(
            os.path.join(self.scraped_folder, next(iter(self.new_folders)))
        ):
            if new_file.endswith(".csv"):
                with open(
                    os.path.join(
                        self.scraped_folder, next(iter(self.new_folders)), new_file
                    ),
                    "r",
                    newline="",
                    encoding=DATA["encoding"],
                ) as csvfile:
                    reader = csv.reader(csvfile)
                    counted_rows += len(list(reader)) - 1

        expected_rows = self.search_criteria["scraped_offers_cap"]
        self.assertEqual(
            counted_rows,
            expected_rows,
            f"Expected {expected_rows} data rows in {new_file}, found {counted_rows}.",
        )

    def _dump_html(self, filename: str) -> None:
        """Dumps the current HTML of the page to a file."""

        html_content = self.driver.page_source
        pretty_html = BeautifulSoup(html_content, "html.parser").prettify()
        log_folder = "logs"
        if not os.path.exists(log_folder):
            os.mkdir(log_folder)
        filepath = os.path.join(log_folder, filename)
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(pretty_html)


if __name__ == "__main__":
    unittest.main()
