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

from pipeline.stages.d_data_visualizing.translations.localization._english import (
    english,
)
from pipeline.stages.d_data_visualizing.translations.localization._polish import polish


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
