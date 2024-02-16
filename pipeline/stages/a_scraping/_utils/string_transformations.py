"""
This module provides utility functions for path and URL formatting in the context of web scraping. 
It includes a function to sanitize file system paths by normalizing them to a standard format, 
and another function to transform location strings into a URL-friendly format.
"""

# Standard imports
import os
import urllib.parse


def sanitize_path(path: str) -> str:
    """
    Sanitizes the given path by normalizing it.

    Args:
        path (str): The path to be sanitized.

    Returns:
        str: The sanitized path.
    """
    return os.path.normpath(path)


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
