"""
This module defines the main functionality for running and managing a data pipeline,
which includes executing various stages like scraping, cleaning, and presenting data through a Streamlit app.
It manages the execution flow based on the presence or absence of data files for specific stages,
decides on skipping stages when necessary, and updates the pipeline configuration dynamically.
It also integrates local components for specific pipeline functionalities, 
such as managing configurations, logging and printing, subprocess management,
error handling, and Streamlit app management.
"""

# Standard library imports
import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Set

# Local imports
from pipeline.config._conf_file_manager import ConfigManager
from pipeline.components.logger import log_and_print
from pipeline.components.pipeline_services import (
    check_new_csv_files,
    get_existing_folders,
    get_pipeline_error_message,
)
from pipeline.components.exceptions import PipelineError
from pipeline.components.subprocess import run_stage
from pipeline.components.streamlit_manager import handle_streamlit_app


def run_pipeline(_stages: list[str], args: argparse.Namespace):
    """
    Executes the defined pipeline stages.

    Args:
        _stages (List[str]): A list of stage names to run.
        args (argparse.Namespace): The parsed command-line arguments required for the stages.
    """
    data_raw_dir = Path("data") / "raw"
    config_file = ConfigManager("run_pipeline.conf")

    log_and_print("Starting pipeline execution...")

    for stage in _stages:
        skip_stage = is_relevant_cleaning_stage(stage) and decide_skip_based_on_files(
            stage, data_raw_dir, config_file
        )
        if skip_stage:
            continue

        log_and_print(f"Running {stage}...")
        try:
            manage_and_run_stage(stage, args, data_raw_dir, config_file)

        except PipelineError as e:
            log_and_print(f"Error running {stage}: {e}", logging.ERROR)
            break  # Exit the loop on error

    else:
        log_and_print("Pipeline execution completed.")
        sys.exit(0)


def decide_skip_based_on_files(
    stage: str, data_raw_dir: Path, config_file: ConfigManager
) -> bool:
    """
    Determines if a cleaning stage for OLX or Otodom should be skipped based on the
    presence of the respective data files.

    Args:
        stage (str): The name of the current pipeline stage.
        data_raw_dir (Path): The directory where raw data is stored.
        config_file (ConfigManager): A configuration manager instance
                                     to access configuration values.

    Returns:
        bool: True if the stage should be skipped, False otherwise.

    Raises:
        PipelineError: If neither OLX nor Otodom data files are found.
        ValueError: If the stage is not supported.
    """

    MARKET_OFFERS_TIMEPLACE = config_file.read_value("MARKET_OFFERS_TIMEPLACE")
    data_scraped_dir = data_raw_dir / MARKET_OFFERS_TIMEPLACE
    olx_exists = any(data_scraped_dir.glob("olx.pl.csv"))
    otodom_exists = any(data_scraped_dir.glob("otodom.pl.csv"))

    if not olx_exists and not otodom_exists:
        message = get_pipeline_error_message(data_scraped_dir)
        log_and_print(message, logging.ERROR)
        raise PipelineError(message)

    _stages = {"OLX": "a_cleaning_OLX", "otodom": "b_cleaning_otodom"}

    if not any(stage_identifier in stage for stage_identifier in _stages.values()):
        message = f"Unsupported stage: {stage}"
        log_and_print(message, logging.ERROR)
        raise ValueError(message)

    if _stages["OLX"] in stage and not olx_exists:
        log_and_print("Skipping OLX cleaning due to missing olx.pl.csv file.")
        return True

    if _stages["otodom"] in stage and not otodom_exists:
        log_and_print("Skipping Otodom cleaning due to missing otodom.pl.csv file.")
        return True

    return False


def is_relevant_cleaning_stage(stage: str) -> bool:
    """
    Determines if the given stage is a cleaning stage for OLX or Otodom and should be skipped.

    Args:
        stage (str): The name of the current pipeline stage.

    Returns:
        bool: True if the stage is a cleaning stage for OLX or Otodom and should be skipped,
              False otherwise.
    """
    is_cleaning_stage = "b_cleaning" in stage
    is_relevant_platform = "OLX" in stage or "otodom" in stage
    return is_cleaning_stage and is_relevant_platform


def manage_and_run_stage(
    stage: str,
    args: argparse.Namespace,
    data_raw_dir: Path,
    config_file: ConfigManager,
):
    """
    Manage a given pipeline stage based on its type (scraping, streamlit app, etc.).
    And runs the stage with the provided arguments.
    Also updates the configuration file after scraping based on the newly created folders.

    Args:
        stage (str): The name of the stage to process.
        args (Any): Arguments required for the stage.
        data_raw_dir (Path): Path to the directory where raw data is stored.
        config_file (ConfigManager): The configuration manager for accessing
                                     and updating config values.
    """
    if "a_scraping" in stage:
        scraping_args = [
            "--location_query",
            args.location_query,
            "--area_radius",
            args.area_radius,
            "--scraped_offers_cap",
            args.scraped_offers_cap,
        ]

        initial_folders = get_existing_folders(data_raw_dir)

        run_stage(stage, os.environ, scraping_args)
        update_after_scraping(data_raw_dir, config_file, initial_folders)
    elif "streamlit_app" in stage:
        handle_streamlit_app(stage)
    else:
        run_stage(stage, os.environ)


def update_after_scraping(
    data_raw_dir: Path, config_file: ConfigManager, initial_folders: Set[str]
):
    """
    Updates the configuration file after scraping based on the newly created folders.

    Args:
        data_raw_dir (Path): Path to the directory where raw data is stored.
        config_file (ConfigManager): The configuration manager for accessing
                                     and updating config values.
        initial_folders (Set[str]): A set of folder names present before the scraping stage.
    """

    new_folder = check_new_csv_files(data_raw_dir, initial_folders)

    if new_folder and new_folder != config_file.read_value("MARKET_OFFERS_TIMEPLACE"):

        log_and_print(
            f"New folder found: {new_folder}. Updating the configuration file."
            f'Writing "MARKET_OFFERS_TIMEPLACE"={new_folder} to {config_file.config_path}'
        )

        config_file.write_value("MARKET_OFFERS_TIMEPLACE", new_folder)
    else:
        log_and_print(
            "No new folders were found after scraping. Exiting the pipeline.",
            logging.WARNING,
        )
        sys.exit(1)
