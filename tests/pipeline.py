"""
This module contains the implementation of 
a data processing pipeline and associated dashboard functionalities. 

The core components include:
- A pipeline process for data transformation, training and loading.
- A dashboard interface for monitoring and interacting with the pipeline's output.
"""

# Standard imports
from pathlib import Path
from typing import List
import logging
import os
import requests
import shutil
import subprocess
import time
import unittest

# Third-party imports
import pandas as pd
import psutil

# Local imports
from pipeline.config._conf_file_manager import ConfigManager


class TestPipelineAndDashboard(unittest.TestCase):
    """
    Facilitates testing of the pipeline
    and dashboard functionalities to ensure system integrity and performance.

    This class provides a set of methods to automate the testing of
    data processing pipelines and their corresponding dashboards.
    It aims to identify potential issues and performance bottlenecks
    within the pipeline processing and dashboard visualization components.
    """

    @classmethod
    def setUpClass(cls):
        """
        Sets up the test environment by creating the necessary folders, starting the pipeline,
        and configuring logging.
        """
        cls.log_folder = Path("log")
        cls.log_file = cls.log_folder / "test_pipeline.log"
        cls.verify_and_create_folder(cls.log_folder)
        cls.configure_logging()

        cls.data_folder = Path("data")
        cls.raw_folder = cls.data_folder / "raw"
        cls.cleaned_folder = cls.data_folder / "cleaned"
        cls.model_folder = Path("model")
        cls.verify_folders_exist(
            [cls.data_folder, cls.raw_folder, cls.cleaned_folder, cls.model_folder]
        )

        cls.pipeline_config = ConfigManager("run_pipeline.conf")
        cls.pre_existing_conditions = cls.get_pre_existing_conditions()

        cls.start_pipeline()

    @classmethod
    def verify_and_create_folder(cls, folder: Path):
        """
        Verifies that the specified folder exists, and creates it if it does not.

        Args:
            folder (Path): The folder to verify and potentially create.
        """
        if not folder.exists():
            folder.mkdir(parents=True)

    @classmethod
    def configure_logging(cls):
        """
        Configures logging to write messages to a file in the specified log folder.
        """
        logging.basicConfig(
            filename=str(cls.log_file),
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

    @classmethod
    def verify_folders_exist(cls, folders: List[Path]):
        """
        Verifies that the specified folders exist.

        Args:
            folders (List[Path]): The folders to verify.

        Raises:
            FileNotFoundError: If a folder does not exist.
        """
        for folder in folders:
            if not folder.exists():
                message = f"The folder {folder} does not exist."
                logging.error(message)
                raise FileNotFoundError(message)

    @staticmethod
    def get_folder_paths(folder: Path):
        """
        Returns the paths of the folders in the specified directory.

        Args:
            folder (Path): The directory to search for folders.

        Returns:
            List[str]: The paths of the folders in the specified directory.
        """
        return [str(folder) for folder in folder.glob("*") if folder.is_dir()]

    @classmethod
    def start_pipeline(cls):
        """
        Starts the pipeline by running the `run_pipeline.py` script
        with the specified location query, area radius, and scraped offers cap.
        """
        command = (
            "python pipeline/run_pipeline.py --location_query"
            "'Warszawa' --area_radius 25 --scraped_offers_cap 100"
        )
        # pylint: disable=consider-using-with
        cls.process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        logging.info("Pipeline process started with PID: %s", cls.process.pid)
        cls.wait_for_dashboard_to_start()

    @classmethod
    def get_pre_existing_conditions(cls):
        """
        Returns the pre-existing conditions in the raw, cleaned, and model directories.
        """
        return {
            "MARKET_OFFERS_TIMEPLACE": cls.pipeline_config.read_value(
                "MARKET_OFFERS_TIMEPLACE"
            ),
            "raw_folders": cls.get_folder_paths(cls.raw_folder),
            "cleaned_folders": cls.get_folder_paths(cls.cleaned_folder),
            "model_folders": cls.get_folder_paths(cls.model_folder),
        }

    @classmethod
    def wait_for_dashboard_to_start(cls):
        """
        Waits for the dashboard to start by checking if the expected port is open.
        Raises a TimeoutError if the dashboard does not start within 30 minutes.
        """
        port = os.getenv("STREAMLIT_SERVER_PORT")
        if not port:
            message = "STREAMLIT_SERVER_PORT environment variable not set"
            logging.error(message)
            raise ValueError(message)

        start_time = time.time()
        half_hour = 30 * 60

        while True:
            if (time.time() - start_time) > half_hour:
                message = "Dashboard did not start within 30 minutes"
                logging.error(message)
                raise TimeoutError(message)

            try:
                response = requests.get(f"http://localhost:{port}", timeout=5)
                if response.status_code == 200:
                    message = "Dashboard is up and running."
                    logging.info(message)
                    print(message)
                    break
            except (requests.ConnectionError, requests.Timeout) as error:
                message = f"Connection attempt failed: {error}"
                logging.error(message)
                print(message)
                time.sleep(5)  # Wait for 5 seconds before trying again

    def test_scraping_stage_ran_successfully(self):
        """
        Validates the presence of expected files in the new folder created by the scraping stage.
        """

        current_raw_folder_paths = [
            str(folder) for folder in self.raw_folder.glob("*") if folder.is_dir()
        ]
        self.assert_stage_success(
            stage="scraping",
            current_folder_paths=current_raw_folder_paths,
            pre_existing_folders=self.pre_existing_conditions["raw_folders"],
            expected_files=["olx.pl.csv", "otodom.pl.csv"],
        )

    def test_cleaning_stage_ran_successfully(self):
        """
        Validates the presence of expected files in the new folder created by the cleaning stage.
        """
        current_clean_folder_paths = [
            str(folder) for folder in self.raw_folder.glob("*") if folder.is_dir()
        ]
        self.assert_stage_success(
            stage="cleaning",
            current_folder_paths=current_clean_folder_paths,
            pre_existing_folders=self.pre_existing_conditions["clean_folders"],
            expected_files=[
                "olx.pl.csv",
                "otodom.pl.csv",
                "map_df.csv",
                "combined_df.csv",
            ],
        )

    def assert_stage_success(
        self,
        stage: str,
        current_folder_paths: List[str],
        pre_existing_folders: List[str],
        expected_files: List[str],
    ):
        """
        Validates the presence of expected files in the new folder created by a pipeline stage.
        """
        valid_csv_files = self.verify_and_collect_new_stage_files(
            stage, current_folder_paths, pre_existing_folders, expected_files
        )
        self.are_cvs_files_valid(valid_csv_files)

    def verify_and_collect_new_stage_files(
        self,
        stage: str,
        current_folder_paths: List[str],
        pre_existing_folders: List[str],
        expected_files: List[str],
    ):
        """
        Validates the presence of expected files in the new folder created by a pipeline stage.

        Args:
            stage (str): The name of the pipeline stage.
            current_folder_paths (List[str]): The current folder paths in the pipeline stage.
            pre_existing_folders (List[str]): The pre-existing folder paths in the pipeline stage.
            expected_files (List[str]): The expected file names in the new folder.

        Returns:
            List[Path]: The valid CSV files in the new folder.
        """

        new_folders = list(set(current_folder_paths) - set(pre_existing_folders))

        # Assert exactly one new folder is created
        folders_count = len(new_folders)
        message = (
            f"{stage.capitalize()} stage not create exactly one new folder as expected."
        )
        self.assertTrue(
            folders_count == 1,
            message,
        )
        if folders_count != 1:
            logging.error(message)

        new_folder = Path(new_folders[0])

        # Check and collect existence of expected files
        files_existence = {
            file_name: (Path(new_folder) / file_name).exists()
            for file_name in expected_files
        }

        # The map_df and combined_df files depend on the presence
        # of either olx.pl.csv or otodom.pl.csv files.
        are_neccecery_files_present = any(files_existence.values())
        message = (
            f"{stage.capitalize()} stage did not create any of the expected files"
            f"in the new folder: {new_folder}"
        )
        self.assertTrue(
            are_neccecery_files_present,
            message,
        )
        if not are_neccecery_files_present:
            logging.error(message)

        # Validate CSV files
        valid_csv_files = [
            new_folder / file_name
            for file_name, exists in files_existence.items()
            if exists
        ]

        return valid_csv_files

    def test_modeling_stage_ran_successfully(self):
        """
        Validates the presence of expected files in the new folder created by the modeling stage.
        """
        current_model_folder_paths = [
            str(folder) for folder in self.model_folder.glob("*") if folder.is_dir()
        ]
        self.verify_and_collect_new_stage_files(
            stage="modeling_developing",
            current_folder_paths=current_model_folder_paths,
            pre_existing_folders=self.pre_existing_conditions["model_folders"],
            expected_files=["model.pkl"],
        )

    def test_dashboard_is_running(self):
        """
        Tests if the dashboard is running at the expected address.
        Fails the test if the dashboard is not running.
        """
        port = os.getenv("STREAMLIT_SERVER_PORT")
        if not port:
            message = "STREAMLIT_SERVER_PORT environment variable not set"
            logging.error(message)
            self.fail(message)

        try:
            response = requests.get(f"http://localhost:{port}", timeout=5)
            is_OK = response.status_code == 200
            message = "The dashboard is not running at the expected address."
            self.assertTrue(
                is_OK,
                message,
            )
            if not is_OK:
                logging.error(message)

        except requests.ConnectionError:
            message = "The dashboard is not running."
            logging.error(message)
            self.fail(message)

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
                message = (
                    "The dashboard process did not stop within 5 seconds"
                    "after sending 'stop'."
                )
                logging.error(message)
                self.fail(message)

        except (IOError, OSError) as specific_e:
            message = f"Failed to communicate with the dashboard process: {specific_e}"
            logging.error(message)
            self.fail(message)
        except Exception as unexpected_e:  # pylint: disable=broad-except
            # Catching broad exception due to the need to fail the test for any unexpected issue
            message = f"Unexpected error when trying to stop the dashboard process: {unexpected_e}"
            logging.error(message)
            self.fail(message)

    def are_cvs_files_valid(self, csv_files: list[Path]):
        """
        Validates the CSV files in the list.

        Args:
            csv_files (list[Path]): The CSV files to validate.

        Raises:
            AssertionError: If a CSV file is empty or cannot be read.
        """

        for csv in csv_files:
            if csv.exists():
                try:
                    df = pd.read_csv(csv)
                    if df.empty:
                        message = f"The CSV file {csv} is empty."
                        logging.error(message)
                        self.fail(message)

                except pd.errors.EmptyDataError:
                    message = f"The CSV file {csv} is empty."
                    logging.error(message)
                    self.fail(message)

                except Exception as unexpected_e:
                    message = (
                        "Unexpected error.\n"
                        f"Failed to read or validate the CSV file {csv}:\n{unexpected_e}"
                    )
                    logging.error(message)
                    self.fail(message)

    @classmethod
    def tearDownClass(cls):
        """
        Cleans up the files and processes created during the tests,
        and resets configurations to their original state.
        """
        # Check if the process was started and is still running before attempting to terminate it
        if hasattr(cls, "process") and cls.process:
            cls.kill_parent_and_its_children_processes()

        # Clean up newly created files if the initial condition checks were set up
        if hasattr(cls, "pre_existing_conditions"):
            cls.clean_up_newly_created_files()

        # Reset the configuration to its pre-existing state if it was modified
        if (
            hasattr(cls, "pre_existing_conditions")
            and "MARKET_OFFERS_TIMEPLACE" in cls.pre_existing_conditions
        ):
            cls.set_timeplace_config_to_pre_existing_state()

        # Call the superclass method to ensure any additional teardown logic is executed
        super().tearDownClass()

    @classmethod
    def set_timeplace_config_to_pre_existing_state(cls):
        """
        Sets the `MARKET_OFFERS_TIMEPLACE` configuration
        in the `run_pipeline.conf`file
        back to its original state.
        """
        cls.pipeline_config.write_value(
            "MARKET_OFFERS_TIMEPLACE",
            cls.pre_existing_conditions["MARKET_OFFERS_TIMEPLACE"],
        )

    @classmethod
    def kill_parent_and_its_children_processes(cls):
        """
        Kills the parent and its children processes.
        """
        try:
            parent = psutil.Process(cls.process.pid)
        except psutil.NoSuchProcess:
            return  # Process already terminated

        for child in parent.children(recursive=True):
            child.terminate()
            child.wait()

        parent.terminate()
        parent.wait()

    @classmethod
    def clean_up_newly_created_files(cls):
        """
        Deletes new folders and their files created during the tests in the
        raw, cleaned, and model directories.
        """
        folder_map = {
            "raw_folders": cls.raw_folder,
            "cleaned_folders": cls.cleaned_folder,
            "model_folders": cls.model_folder,
        }

        for folder_type, initial_folders_set in cls.pre_existing_conditions.items():

            if folder_type in folder_map:

                stage_folder = folder_map[folder_type]
                current_folders = set(cls.get_folder_paths(stage_folder))

                new_folders = current_folders - set(initial_folders_set)

                for folder_path in new_folders:
                    try:
                        shutil.rmtree(Path(folder_path))
                        message = f"Deleted new folder: {folder_path}"
                        logging.info(message)
                        print(message)
                    except Exception as unexpected_e:
                        message = (
                            "Unexecpted error.\n"
                            f"Failed to delete {folder_path}: {unexpected_e}"
                        )
                        logging.error(message)
                        print(message)


if __name__ == "__main__":
    unittest.main()
