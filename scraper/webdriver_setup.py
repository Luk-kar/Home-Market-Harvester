"""
Module for setting up and configuring the Selenium WebDriver 
for web scraping, 
with options for headless browsing and 
custom user agents.
"""

# third-party imports
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Local imports
from scraper.config import LOGGING, WEBDRIVER


class WebDriverSetupError(Exception):
    """Exception raised for errors in WebDriver setup."""


def get_driver():
    """
    Initializes and returns a Selenium WebDriver with specified options.

    This function sets up a Chrome WebDriver based on
      the configuration provided in WEBDRIVER.
      It includes options like headless browsing,
      window maximization, and user-agent customization.
      If 'auto_install' is True in the configuration,
      the WebDriver is automatically installed using WebDriverManager.
      Otherwise, it uses the specified driver path.

    Raises:
        WebDriverSetupError: If the WebDriver path is not found
        or neither path nor auto-install option is provided.

    Returns:
        WebDriver: An instance of Selenium WebDriver
        configured as per the specified options.
    """

    options = webdriver.ChromeOptions()

    if WEBDRIVER["maximize_window"]:
        options.add_argument("start-maximized")

    if WEBDRIVER["user_agent"] == "random":
        options.add_argument(f"user-agent={UserAgent().random}")

    if WEBDRIVER["headless"] and not LOGGING["debug"]:
        options.add_argument("--headless=new")

    if WEBDRIVER["ignore_certificate_errors"]:
        options.add_argument("--ignore-certificate-errors")

    if WEBDRIVER["auto_install"]:
        # There could some issues:
        # https://stackoverflow.com/questions/76932496/webdrivermanager-setup-failing-to-download-chromedriver-116
        service = ChromeService(ChromeDriverManager().install())
    elif WEBDRIVER["path"]:
        # https://stackoverflow.com/questions/77614587/where-can-i-find-chromedriver-119
        # The drivers: https://stackoverflow.com/a/76939681/12490791
        service = ChromeService(WEBDRIVER["path"])
    else:
        raise WebDriverSetupError("No webdriver path or auto-install option provided")

    return webdriver.Chrome(service=service, options=options)
