"""
This module contains the Translation class, 
a singleton design pattern implementation for managing translations 
in a dashboard application.

The Translation class is responsible for 
handling language settings and retrieving appropriate translation strings. 
It utilizes a dictionary of translations imported from `localization_content.py`, 
which includes various language options defined in the Languages class.

The singleton pattern ensures that there is only a single instance 
of the Translation class throughout the application, 
providing a consistent and centralized translation management system.

Usage:
    To use the Translation class, 
    set the desired language using the set_language method, 
    and retrieve translation strings 
    using the class instance like a dictionary.

Example:
    Translation.set_language("Polish")
    print(Translation()["chart"]["title"])

Methods:
    set_language: Sets the current language for translations.

Raises:
    KeyError: If the key is not found in the translations for the current language.

Note:
    This module depends on `localization_content.py` 
    from the `d_data_visualizing.translations` package for translation data.
"""

# Local imports
from pipeline.src.d_data_visualizing.translations.localization.content import (
    translations,
    Languages,
)


class Translation:
    """
    A singleton class responsible for managing translations in the application.

    Attributes:
        _instance: Holds the singleton instance of the Translation class.
        _language: The current language set for translations.
        _texts: The dictionary containing all translations.
    """

    _instance = None
    _language = Languages.ENGLISH
    _texts = translations

    def __new__(cls):
        """
        Ensures that only one instance of the Translation class is created.
        Returns the singleton instance of the Translation class.
        """
        if cls._instance is None:
            cls._instance = super(Translation, cls).__new__(cls)
        return cls._instance

    @classmethod
    def set_language(cls, language: str):
        """
        Sets the current language for translations.

        Args:
            language (str): The language code to set as the current language.
        """
        cls._language = language

    def __getitem__(self, key: str):
        """
        Retrieves a translation based on the provided key for the current language.

        Args:
            key (str): The key for the desired translation string.

        Returns:
            The translation string corresponding to the provided key.

        Raises:
            KeyError: If the key is not found in the translations for the current language.
        """

        try:
            return self._texts[self._language][key]
        except KeyError as error:
            raise KeyError(
                f"Missing translation key: '{key}' in language '{self._language}'"
                + f"\n{self._texts[self._language]}"
            ) from error
