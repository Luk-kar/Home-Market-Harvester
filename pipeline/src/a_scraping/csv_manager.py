"""
This module provides utilities for sanitizing strings 
for file paths and saving data records to CSV files. 
"""

# Standard imports
import csv
import os
import re
from typing import Any

# Local imports
from pipeline.src.a_scraping._utils.string_transformations import sanitize_path
from pipeline.src.a_scraping.config import DATA


def sanitize_for_filepath(string: str):
    """
    Sanitizes a string to make it suitable for use in a file path.

    Args:
        string (str): The string to be sanitized.

    Returns:
        str: The sanitized string.
    """
    without_location_separators = re.sub(r"( +,+)", "_", string)
    without_protocol = re.sub(r"^https?://", "", without_location_separators)
    without_www = re.sub(r"^www\.", "", without_protocol)
    filename_safe_url = re.sub(r"[^\w.]", "_", without_www)
    return filename_safe_url


def save_to_csv(record: dict[str, Any], query_name: str, domain: str, timestamp: str):
    """
    Save a record to a CSV file.

    Args:
        record (dict[str, Any]): The record to be saved.
        query_name (str): The name of the query.
        domain (str): The domain of the data.
        timestamp (str): The timestamp of the data.

    Returns:
        None
    """
    file_name = sanitize_for_filepath(query_name)
    domain_name = sanitize_for_filepath(domain)
    directory = sanitize_path(f"{DATA['folder_scraped_data']}/{timestamp}_{file_name}")
    file_path = sanitize_path(f"{directory}/{domain_name}.csv")

    if not os.path.exists(directory):
        os.makedirs(directory)

    file_exists = os.path.isfile(file_path)

    with open(file_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=record.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(record)
