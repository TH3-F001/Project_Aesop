from common.browser import WebBrowser
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import yaml
import json
from time import sleep
import os
import shutil

class Visla:
    def __init__(self):
        self.home_url = "https://app.visla.us/home"
        self.login_url = "https://app.visla.us/signin"
        self.conf_file = "appdata/visla.yaml"
        # Grab Configuration from visla.yaml

        if not os.path.exists(self.conf_file):
            self.create_config_file()
        
        with open(self.conf_file, 'r') as file:
            self.conf = yaml.safe_load(file)
        self.browser = WebBrowser()


    def find_firefox_binary(self):
        firefox_binary_paths = [
            '/bin/firefox',
            '/usr/bin/firefox',
            '/usr/local/bin/firefox',
            'C:\\Program Files\\Mozilla Firefox\\firefox.exe',
            'C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe'
        ]
        for path in firefox_binary_paths:
            if os.path.exists(path):
                return path

        # If not found, try to locate using which command on Unix-based systems
        firefox_path = shutil.which('firefox')
        if firefox_path:
            return firefox_path
        raise FileNotFoundError("Firefox binary not found. Please install Firefox or specify the binary location.")


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
