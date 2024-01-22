from dashboard.translations.localization._english import english
from dashboard.translations.localization._polish import polish

_checked_translation_keys = False  # Variable to track if the check has been performed


def check_translation_keys(translations: dict):
    """
    Checks if the translation dictionaries have the same keys.
    """
    global _checked_translation_keys
    if not _checked_translation_keys:
        # Get the keys from the first dictionary
        keys_set = set(translations[0].keys())

    # Check if all dictionaries have the same keys
    for translation_dict in translations[1:]:
        if set(translation_dict.keys()) != keys_set:
            # Find the differences in keys
            diff_keys = set(translation_dict.keys()) ^ keys_set
            raise ValueError(
                f"Translation dictionaries have different keys: {diff_keys}"
            )


# Check translation keys when the package is imported
check_translation_keys([english, polish])

# Define the public interface of this module.
# Only symbols listed in __all__ will be imported when using 'from module import *'.
__all__ = ["Languages", "translations"]
