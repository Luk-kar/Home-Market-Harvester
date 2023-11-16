from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from fake_useragent import UserAgent
from config import WEBDRIVER


def get_driver():
    options = webdriver.ChromeOptions()

    if WEBDRIVER["maximize_window"]:
        options.add_argument("start-maximized")

    if WEBDRIVER["user_agent"] == "random":
        options.add_argument(f"user-agent={UserAgent().random}")

    if WEBDRIVER["headless"]:
        options.add_argument("--headless")

    return webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()), options=options
    )
