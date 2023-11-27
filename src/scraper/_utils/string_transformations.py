# Standard imports
import os
import urllib.parse


import os


def sanitize_path(path: str) -> str:
    """
    Sanitizes the given path by normalizing it.

    Args:
        path (str): The path to be sanitized.

    Returns:
        str: The sanitized path.
    """
    return os.path.normpath(path)


import urllib.parse


def transform_location_to_url_format(location: str) -> str:
    """
    Transforms the given location string into URL format.

    Args:
        location (str): The location string to be transformed.

    Returns:
        str: The transformed location string in URL format.
    """
    formatted_location = location.replace(" ", "-")
    encoded_location = urllib.parse.quote(formatted_location, safe="-")
    return encoded_location
