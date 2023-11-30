# Standard imports
import csv
import os
import shutil
import unittest

# Third-party imports
import datetime
from selenium.common.exceptions import WebDriverException
import enlighten

# Local imports
from scraper._utils.selenium_utils import humans_delay
from scraper._utils.string_transformations import transform_location_to_url_format
from scraper.config import DATA, SCRAPER, DOMAINS
from scraper.scrape.olx.process_olx_site_offers import process_domain_offers_olx
from scraper.scrape.process_sites_offers import scrape_offers
from scraper.webdriver_setup import get_driver


class TestScraper(unittest.TestCase):
    def setUp(self):
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

    def tearDown(self):
        if self.new_folders is not None:
            for folder in self.new_folders:
                folder_path = os.path.join(self.scraped_folder, folder)
                shutil.rmtree(folder_path)

        self.new_folders = None

        humans_delay()

    def test_end_to_end(self):
        """
        End-to-End Test: Run the entire script from start to finish.
        """
        try:
            search_criteria = self.search_criteria.copy()
            search_criteria["location_query"] = self.location_query["low_volume"]

            scrape_offers(self.driver, search_criteria)
        except Exception as e:
            self.fail(f"Scrape offers failed with {e}")
        finally:
            self.driver.quit()

        existing_folders_after = set(os.listdir(self.scraped_folder))
        self.new_folders = existing_folders_after - self.existing_folders_before

        self.assertNotEqual(
            self.existing_folders_before,
            existing_folders_after,
            "No new data files were created.",
        )
        self.assertEqual(
            len(self.new_folders),
            1,
            "There should be one folder for all created data.",
        )

        for folder in self.new_folders:
            files = os.listdir(os.path.join(self.scraped_folder, folder))
            self.assertGreaterEqual(
                len(files),
                1,
                f"There should be at least one file in {folder}.",
            )
            for file in files:
                self.assertTrue(
                    file.endswith(".csv"), f"File {file} should be a csv file."
                )

            number_of_data_rows = 0
            for file in files:
                file_path = os.path.join(self.scraped_folder, folder, file)
                with open(
                    file_path, "r", newline="", encoding=DATA["encoding"]
                ) as csvfile:
                    reader = csv.reader(csvfile)
                    rows = list(reader)
                    # Assuming the first row is the header
                    number_of_data_rows = len(rows) - 1
            self.assertTrue(
                search_criteria["scraped_offers_cap"] == number_of_data_rows,
                f"The CSV file {file} should contain rows at the same length as the cap.",
            )

    def test_olx_scrape_offers(self):
        """
        Test: Scrape offers from OLX.
        """
        try:
            search_criteria = self.search_criteria.copy()
            search_criteria["location_query"] = self.location_query["high_volume"]
            offers_cap = search_criteria["scraped_offers_cap"]

            progress = enlighten.Counter(
                desc="Total progress",
                unit="offers",
                color="green",
                total=offers_cap,
            )

            formatted_location = transform_location_to_url_format(
                search_criteria["location_query"]
            )
            url = f'{DOMAINS["olx"]["domain"]}/{DOMAINS["olx"]["category"]}q-{formatted_location}/'
            timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            scraped_urls: set[str] = set()

            humans_delay()
            self.driver.get(url)

            process_domain_offers_olx(
                self.driver, search_criteria, timestamp, progress, scraped_urls
            )
        except Exception as e:
            self.fail(f"Scrape offers failed with {e}")
        finally:
            self.driver.quit()

        existing_folders_after = set(os.listdir(self.scraped_folder))
        self.new_folders = existing_folders_after - self.existing_folders_before

        self.assertNotEqual(
            self.existing_folders_before,
            existing_folders_after,
            "No new data files were created.",
        )
        self.assertEqual(
            len(self.new_folders),
            1,
            "There should be one folder for all created data.",
        )

        for folder in self.new_folders:
            files = os.listdir(os.path.join(self.scraped_folder, folder))
            self.assertGreaterEqual(
                len(files),
                1,
                f"There should be at least one file in {folder}.",
            )
            for file in files:
                self.assertTrue(
                    file.endswith(".csv"), f"File {file} should be a csv file."
                )

            number_of_data_rows = 0
            for file in files:
                file_path = os.path.join(self.scraped_folder, folder, file)
                with open(
                    file_path, "r", newline="", encoding=DATA["encoding"]
                ) as csvfile:
                    reader = csv.reader(csvfile)
                    rows = list(reader)
                    # Assuming the first row is the header
                    number_of_data_rows += len(rows) - 1
            self.assertTrue(
                search_criteria["scraped_offers_cap"] == number_of_data_rows,
                f"The CSV file {file} should contain rows at the same length as the cap.",
            )

    def test_otodom_scrape_offers(self):
        """
        Test: Scrape offers from otodom.com.
        """
        try:
            search_criteria = self.search_criteria.copy()
            search_criteria["location_query"] = self.location_query["high_volume"]

            scrape_offers(self.driver, search_criteria)
        except Exception as e:
            self.fail(f"Scrape offers failed with {e}")
        finally:
            self.driver.quit()

        existing_folders_after = set(os.listdir(self.scraped_folder))
        self.new_folders = existing_folders_after - self.existing_folders_before

        self.assertNotEqual(
            self.existing_folders_before,
            existing_folders_after,
            "No new data files were created.",
        )
        self.assertEqual(
            len(self.new_folders),
            1,
            "There should be one folder for all created data.",
        )

        for folder in self.new_folders:
            files = os.listdir(os.path.join(self.scraped_folder, folder))
            self.assertGreaterEqual(
                len(files),
                1,
                f"There should be at least one file in {folder}.",
            )
            for file in files:
                self.assertTrue(
                    file.endswith(".csv"), f"File {file} should be a csv file."
                )

            number_of_data_rows = 0
            for file in files:
                file_path = os.path.join(self.scraped_folder, folder, file)
                with open(
                    file_path, "r", newline="", encoding=DATA["encoding"]
                ) as csvfile:
                    reader = csv.reader(csvfile)
                    rows = list(reader)
                    # Assuming the first row is the header
                    number_of_data_rows += len(rows) - 1

            self.assertTrue(
                search_criteria["scraped_offers_cap"] == number_of_data_rows,
                f"The CSV file {file} should contain rows at the same length as the cap.",
            )


if __name__ == "__main__":
    unittest.main()
