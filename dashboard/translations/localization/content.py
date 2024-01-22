"""
This module defines the language options 
and translations used in the dashboard application.

It contains the Languages class, an enum-like construct that provides 
a clear and standardized way to refer to the different languages supported by the application. 
Additionally, the module includes a dictionary named 'translations' 
that maps language codes to their respective translation strings.

The 'translations' dictionary is structured hierarchically, 
with each top-level key representing a language (e.g., 'English', 'Polish'). 
These keys map to nested dictionaries containing 
the relevant translation strings for various text elements in the application, s
uch as labels, messages, and titles.

Attributes:
    Languages: A class containing language constants used throughout the application.
    translations (dict): A dictionary mapping language codes 
                         to their respective translation strings.

Example:
    To access a translation string for the English welcome message:
        translations[Languages.ENGLISH]["welcome"]
"""

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


check_translation_keys([english, polish])


class Languages:
    """
    Enum-like class containing language codes used in the application.

    Attributes:
        ENGLISH (str): Represents the English language.
        POLISH (str): Represents the Polish language.
    """

    ENGLISH = "English"
    POLISH = "Polish"


"""
Dictionary containing the translations for different languages.

Each language code maps to a dictionary of translation strings.
The dictionary is structured with the top-level keys 
as language names ('English', 'Polish', etc.),
each mapping to a nested dictionary containing the relevant translation strings.
"""
translations = {
    "English": english,
    "Polish": polish,
}
