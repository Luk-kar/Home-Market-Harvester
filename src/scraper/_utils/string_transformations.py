# Standard imports
import os
import urllib.parse


def sanitize_path(path: str) -> str:
    """Sanitize the path to the current OS."""
    return os.path.normpath(path)


def transform_location_to_url_format(location: str) -> str:
    formatted_location = location.replace(" ", "-")

    encoded_location = urllib.parse.quote(formatted_location, safe="-")

    return encoded_location
