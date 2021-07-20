from news_parser.settings import FIREFOX_DRIVER

from selenium import webdriver
from selenium.webdriver.firefox.options import Options


# Open session in browser using Webdriver
def selenium_driver(browser_driver: webdriver =None, headless=False):
    """
    :param browser_driver:
    :param news_source:
    :param headless:
    :return:
    """
    browser_driver = browser_driver or FIREFOX_DRIVER

    options = Options()
    options.headless = headless

    return webdriver.Firefox(options=options, executable_path=browser_driver)
