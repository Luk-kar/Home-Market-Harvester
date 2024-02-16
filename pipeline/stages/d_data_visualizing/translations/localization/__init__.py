from pipeline.stages.d_data_visualizing.translations.localization._english import (
    english,
)
from pipeline.stages.d_data_visualizing.translations.localization._polish import polish

_checked_translation_keys = False  # Variable to track if the check has been performed


def check_translation_keys(translations: list[dict]):
    """
    Recursively checks if all provided translation dictionaries have the same keys.
    """
    first_dict = translations[0]
    for other_dict in translations[1:]:
        compare_dicts(first_dict, other_dict)


def compare_dicts(dict1: dict, dict2: dict, parent_key=""):
    """
    Recursively compares the keys of two dictionaries.
    """
    for key in dict1:
        if key not in dict2:
            raise ValueError(
                f"Key {parent_key + key} is missing in the second dictionary."
            )
        if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            compare_dicts(dict1[key], dict2[key], parent_key + key + ".")

    for key in dict2:
        if key not in dict1:
            raise ValueError(
                f"Key {parent_key + key} is missing in the first dictionary."
            )


# Check translation keys when the package is imported
check_translation_keys([english, polish])

# Define the public interface of this module.
# Only symbols listed in __all__ will be imported when using 'from module import *'.
__all__ = ["Languages", "translations"]
