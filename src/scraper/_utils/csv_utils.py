# csv, _csv are built-in modules

# Standard imports
import csv
import os
import re

# Local imports
from _utils.string_transformations import sanitize_path
from config import DATA


def sanitize_for_filepath(string: str):
    without_location_separators = re.sub(r"( +,+)", "_", string)

    without_protocol = re.sub(r"^https?://", "", without_location_separators)

    without_www = re.sub(r"^www\.", "", without_protocol)

    filename_safe_url = re.sub(r"[^\w.]", "_", without_www)

    return filename_safe_url


def save_to_csv(record, query_name, domain, timestamp):
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
