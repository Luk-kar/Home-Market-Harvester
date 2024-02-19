# Standard imports
import unittest
import subprocess
import requests
import time
import os
from pathlib import Path

# Third-party imports
import pandas as pd
import psutil

# Local imports
from pipeline.config._conf_file_manager import ConfigManager


class TestPipelineAndDashboard(unittest.TestCase):
    pipeline_config = ConfigManager("run_pipeline.conf")

    data_folder = Path("data")
    clean_folder = data_folder / "raw"
    cleaned_folder = data_folder / "cleaned"
    model_folder = Path("model")

    for folder in [data_folder, clean_folder, cleaned_folder, model_folder]:
        if not folder.exists():
            raise FileNotFoundError(f"The folder {folder} does not exist.")

    # check existing folders in raw_folder and cleaned_folder
    raw_folder_paths = [
        str(folder) for folder in clean_folder.glob("*") if folder.is_dir()
    ]
    cleaned_folder_paths = [
        str(folder) for folder in cleaned_folder.glob("*") if folder.is_dir()
    ]
    model_folder_paths = [
        str(folder) for folder in model_folder.glob("*") if folder.is_dir()
    ]

    pre_existing_conditions = {
        "MARKET_OFFERS_TIMEPLACE": pipeline_config.read_value(
            "MARKET_OFFERS_TIMEPLACE"
        ),
        "raw_folders": raw_folder_paths,
        "cleaned_folders": cleaned_folder_paths,
        "model_folders": model_folder_paths,
    }

    scraped_time_place = None

    @classmethod
    def setUpClass(cls):

        start_pipeline_command = "python pipeline/run_pipeline.py --location_query 'Warszawa' --area_radius 25 --scraped_offers_cap 100"
        cls.command = start_pipeline_command
        cls.process = subprocess.Popen(
            cls.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        cls.wait_for_dashboard_to_start()

    def wait_for_dashboard_to_start(self):
        """
        Waits for the Streamlit dashboard to start by checking if the server is running.
        """

        streamlit_port_key = "STREAMLIT_SERVER_PORT"
        port = os.getenv(streamlit_port_key)
        if not port:
            raise ValueError(f"{streamlit_port_key} environment variable not set")

        is_pipeline_finished = False
        while not is_pipeline_finished:
            time.sleep(1)

            response = requests.get(f"http://localhost:{port}")

            OK_response = 200
            if response.status_code == OK_response:
                is_pipeline_finished = True
                time.sleep(
                    5
                )  # Wait a bit longer to ensure the dashboard is fully loaded

    @classmethod
    def tearDownClass(cls):
        """
        Cleans up after test execution by terminating the main pipeline process and all its child processes.

        This method ensures that all resources used by the pipeline and any associated processes,
        such as the Streamlit dashboard, are properly released after tests are completed.
        It uses the `psutil` library to identify and terminate the main process along with any child processes,
        preventing resource leaks and ensuring a clean test environment for subsequent tests.

        Terminating the processes involves sending a terminate signal
        to each child process recursively before terminating the main process itself.
        The method then waits for the main process to exit,
        ensuring that all processes have been cleanly shut down.
        """
        try:
            parent = psutil.Process(cls.process.pid)
        except psutil.NoSuchProcess:
            return  # Process already terminated

        if parent.is_running():
            # Kill all children processes of the pipeline process
            for child in parent.children(recursive=True):
                child.terminate()
                child.wait()  # Wait for the child process to be terminated

            parent.terminate()  # Terminate the main process
            parent.wait()  # Wait for the main process to be terminated

    def test_scraping_stage_ran_successfully(self):
        current_raw_folder_paths = [
            str(folder) for folder in self.clean_folder.glob("*") if folder.is_dir()
        ]
        pre_existing_raw_folders = self.pre_existing_conditions["raw_folders"]
        new_raw_folders = list(
            set(current_raw_folder_paths) - set(pre_existing_raw_folders)
        )

        self.assertTrue(
            len(new_raw_folders) == 1,
            (
                "Scraping stage did not create a folder in the raw data folder.\n"
                f"The raw data folder {self.pre_existing_conditions['raw_folder']}\n"
                f"new_raw_folders:\n{new_raw_folders}\n"
            ),
        )

        new_folder = Path(new_raw_folders[0])

        olx_csv = new_folder / "olx.pl.csv"
        oto_dom_csv = new_folder / "otodom.pl.csv"

        olx_exists = olx_csv.exists()
        oto_dom_exists = oto_dom_csv.exists()

        self.assertTrue(
            olx_exists or oto_dom_exists,
            (
                "Scraping stage did not create a file in the new folder in the raw data folder.\n"
                f"The new folder:\n{new_folder}\n"
            ),
        )

        self.are_cvs_files_valid([olx_csv, oto_dom_csv])

    def are_cvs_files_valid(self, csv_files: list[Path]):

        for csv in csv_files:
            if csv.exists():
                try:
                    df = pd.read_csv(csv)
                    if df.empty:
                        self.fail(f"The CSV file {csv} is empty.")

                except pd.errors.EmptyDataError:
                    self.fail(f"The CSV file {csv} is empty.")

                except Exception as error:
                    self.fail(
                        f"Failed to read or validate the CSV file {csv}:\n{error}"
                    )

    def test_scraping_stage_ran_successfully(self):
        current_clean_folder_paths = [
            str(folder) for folder in self.clean_folder.glob("*") if folder.is_dir()
        ]
        pre_existing_clean_folders = self.pre_existing_conditions["clean_folders"]
        new_clean_folders = list(
            set(current_clean_folder_paths) - set(pre_existing_clean_folders)
        )

        self.assertTrue(
            len(new_clean_folders) == 1,
            (
                f"Cleaning stage did not create a new folder in the cleaned data folder.\n"
                f"The cleaned data folder {self.pre_existing_conditions['cleaned_folder']}\n"
            ),
        )

        new_folder = Path(new_clean_folders[0])

        olx_csv = new_folder / "olx.pl.csv"
        oto_dom_csv = new_folder / "otodom.pl.csv"
        map_df_csv = new_folder / "map_df.csv"
        combined_df_csv = new_folder / "combined_df.csv"

        olx_exists = olx_csv.exists()
        oto_dom_exists = oto_dom_csv.exists()
        map_df_exists = map_df_csv.exists()
        combined_df_exists = combined_df_csv.exists()

        self.assertTrue(
            olx_exists or oto_dom_exists,
            (
                "Scraping stage did not create a file in the new folder in the raw data folder.\n"
                f"The new folder:\n{new_folder}\n"
            ),
        )

        self.assertTrue(
            map_df_exists,
            (
                "Scraping stage did not create a file in the new folder in the raw data folder.\n"
                f"The new folder:\n{new_folder}\n"
            ),
        )

        self.assertTrue(
            combined_df_exists,
            (
                "Scraping stage did not create a file in the new folder in the raw data folder.\n"
                f"The new folder:\n{new_folder}\n"
            ),
        )

        csv_files_to_validate = [
            csv_file
            for csv_file in [
                olx_csv if olx_exists else None,
                oto_dom_csv if oto_dom_exists else None,
                map_df_csv,
                combined_df_csv,
            ]
            if csv_file is not None
        ]

        self.are_cvs_files_valid(csv_files_to_validate)

    def test_close_dashboard(self):
        """
        Tests closing the dashboard by sending a 'stop' command as CLI input.
        Fails the test if the process does not stop within 5 seconds.
        """
        try:
            stop_streamlit_command_stdout = b"stop\n"
            # This requires the subprocess to have been started with stdin=subprocess.PIPE.
            self.process.stdin.write(stop_streamlit_command_stdout)
            self.process.stdin.flush()

            # Give the process some time to respond and terminate.
            time.sleep(5)

            # Check if the process has terminated
            if (
                self.process.poll() is None
            ):  # If poll() returns None, the process is still running
                self.fail(
                    "The dashboard process did not stop within 5 seconds after sending 'stop'."
                )

        except Exception as e:
            self.fail(f"Failed to send 'stop' command to the dashboard process: {e}")

    # You can add more tests here to check specific outcomes or behaviors of your pipeline/dashboard


if __name__ == "__main__":
    unittest.main()
