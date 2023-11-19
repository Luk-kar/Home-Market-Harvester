from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from fake_useragent import UserAgent
from config import WEBDRIVER
import os


def get_driver():
    options = webdriver.ChromeOptions()

    if WEBDRIVER["maximize_window"]:
        options.add_argument("start-maximized")

    if WEBDRIVER["user_agent"] == "random":
        options.add_argument(f"user-agent={UserAgent().random}")

    if WEBDRIVER["headless"]:
        options.add_argument("--headless")

    if WEBDRIVER["auto_install"]:
        # There could some issues:
        # https://stackoverflow.com/questions/76932496/webdrivermanager-setup-failing-to-download-chromedriver-116
        service = ChromeService(ChromeDriverManager().install())
    elif WEBDRIVER["path"]:
        # The drivers: https://stackoverflow.com/a/76939681/12490791
        service = ChromeService(WEBDRIVER["path"])
    else:
        raise Exception("No webdriver path or auto-install option provided")

    return webdriver.Chrome(service=service, options=options)
