from common.browser import WebBrowser
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import yaml
import json
from time import sleep

class Visla:
    def __init__(self):
        self.home_url = "https://app.visla.us/home"
        self.login_url = "https://app.visla.us/signin"

        # Grab Configuration from visla.yaml
        conf_file = "appdata/visla.yaml"
        with open(conf_file, 'r') as file:
            self.conf = yaml.safe_load(file)
        self.browser = WebBrowser()


    def open_homepage(self):
        self.browser.get(self.home_url)
        sleep(1)
        


    def sign_in_for_first_time(self):
        if not self.browser.has_cookies():
            email = self.conf["creds"]["email"]
            pw = self.conf["creds"]["password"]

            self.browser.get(self.login_url)
            print("going to ", self.login_url)
            self.find_and_click_on_google_login()

    def find_and_click_on_google_login(self):
        driver = self.browser.driver
        iframe = driver.find_element(by=By.XPATH, value="//iframe[starts-with(@src, 'https://accounts.google.com/gsi/button')]")
        x = iframe.location['x']
        y = iframe.location['y']
        actions = ActionChains(driver)
        actions.move_by_offset(x , y)  # Adjusting +10 to click just inside the iframe
        actions.click()
        actions.perform()
