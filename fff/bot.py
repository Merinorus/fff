from selenium import webdriver
from selenium.webdriver.firefox.options import Options


class Bot:
    def __init__(self):
        # Use Firefox without GUI
        options = Options()
        options.headless = False
        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(10)
