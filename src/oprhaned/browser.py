from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service


from urllib.parse import urlparse
from time import sleep

import json
import os
import shutil
import random
import pickle
import tldextract
import requests

class WebBrowser:
    def __init__(self, wait_time):
        # Set Filepaths:
        self.geckodriver_path = 'data/geckodriver'
        self.cookie_path = 'data/cookies.pkl'
        self.local_storage_path = 'data/local_storage.json'
        self.sessions_path = 'data/sessions.json'

        #Dictionary used for mapping By enums for data retrieval
        self.by_dict = {
            "xpath": By.XPATH,
            "id": By.ID,
            "name": By.NAME,
            "class_name" : By.CLASS_NAME,
            "css_selector": By.CSS_SELECTOR,
            "link_text": By.LINK_TEXT,
            "partial_link_text": By.PARTIAL_LINK_TEXT,
            "tag_name": By.TAG_NAME
        }
        self.driver = None

        self.wait_time = wait_time



#region General Utilities (Private)
    def _find_firefox_binary(self):
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


    def _get_root_domain(self, url):
        parsed_url = tldextract.extract(self.driver.current_url)
        root_domain = f"{parsed_url.domain}.{parsed_url.suffix}"
        return root_domain


    def _url_is_valid(self, url=""):
        result = False
        try:
            response = requests.head(url, allow_redirects=True)
            result = response.status_code < 400
        except Exception as e:
            print("ERROR: URL is blank or invalid")

        return result

    def _get_locator(self, locator_tag):
        if locator_tag in self.by_dict:
            locator = self.by_dict[locator_tag]
        else:
            print(f"Error {locator_tag} is not in by_dict:\n{self.by_dict}")
        return locator
#endregion

    
#region Browser Control
    def initialize_driver(self):
        print("\tInitializing Driver...")
        # Initialize the Options object
        options = Options()
        # self.options.headless = True
        options.add_argument("--window-size=1920,1080")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0")
        options.binary_location = self._find_firefox_binary()

        # Initialize the Service Object
        service = Service(executable_path=self.geckodriver_path)

        # Initialize the WebDriver with the specified options
        self.driver = webdriver.Firefox(options=options, service=service)
        # Define the WebDriverWait time
        self.wait = WebDriverWait(self.driver, self.wait_time)


    def goto_url(self, url=""):
        if self._url_is_valid(url):
            try:
                if self.driver == None:
                    self.initialize_driver()

                result = self.driver.get(url)
                return result
            except Exception as e:
                print(f"Error while navigating to URL: {url}")
                print(e)

        return None




    def save_and_close(self):
        self.save_local_storage
        self.save_cookies
        self.driver.quit


    def type_keys(self, element: WebElement , msg: str):
        for char in msg:
            element.send_keys(char)
            sleep(random.uniform(0.08, 0.12))


    def type_enter(self, element: WebElement):
        sleep(random.uniform(0.08, 0.12))
        element.send_keys(Keys.RETURN)


    def click(self, element):
        try:
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable(element))
            element.click()
        except Exception as e:
            # Fallback to JavaScript click
            self.driver.execute_script("arguments[0].click();", element)


    def click_center_screen(self):
        window_size = self.driver.get_window_size()
        center_x = window_size['width'] / 2
        center_y = window_size['height'] / 2

        actions = ActionChains(self.driver)
        actions.move_by_offset(center_x, center_y).click().perform()
        actions.move_by_offset(-center_x, -center_y).perform()  # Move back to the origin


    def click_top_screen(self):
        window_size = self.driver.get_window_size()
        center_x = window_size['width'] / 2
        top_y = 5

        actions = ActionChains(self.driver)
        actions.move_by_offset(center_x, top_y).click().perform()
        actions.move_by_offset(-center_x, -top_y).perform()


    def wait_for_element(self, time: float, by: str, tag: str):
        if by in self.by_dict:
            locator = self.by_dict[by]
        else:
            print(f"Error: {by} is not in by_dict:\n{self.by_dict}")
            return None

        wait = WebDriverWait(self.driver, time)
        return wait.until(EC.presence_of_element_located((locator, tag)))

#endregion


#region Browser Data Retrieval
    def get_cookies(self):
        return self.driver.get_cookies()


    def get_element(self, by: str, tag: str):
        locator = self._get_locator(by)
        result = None
        try:
            result = self.wait.until(EC.presence_of_element_located((locator, tag)))
        except TimeoutException as e:
            print(f"Timed Out: {e}")
            return None
        return result

    def get_elements(self, by: str, tag: str):
        locator = self._get_locator(by)
        self.wait.until(EC.presence_of_element_located((locator, tag)))
        return self.driver.find_elements(locator, tag)


    def get_element_text(self, by: str, tag: str):
        locator = self._get_locator(by)
        element =  self.wait.until(EC.presence_of_element_located((locator, tag)))
        return element.text


    def get_child_element(self, parent, by: str, tag: str):
        locator = self._get_locator(by)
        self.wait.until(EC.presence_of_element_located((locator, tag)))
        child_element = parent.find_element(locator, tag)
        return child_element


    def get_current_url(self):
        return self.driver.current_url



    #endregion


#region Cookie Management
    def has_cookies(self, url):
        result = False
        domain = self._get_root_domain(url)

        if os.path.exists(self.cookie_path):
            try:
                cookies = pickle.load(open(self.cookie_path, "rb"))
                for cookie in cookies:
                    if domain in cookie["domain"]:
                        result = True
            except Exception as e:
                return False

        return result


    def save_cookies(self):
        # if not os.path.exists(os.path.dirname(self.cookie_path)):
        #     os.makedirs(os.path.dirname(self.cookie_path))
        #
        cookies = self.driver.get_cookies()
        pickle.dump(cookies, open(self.cookie_path, "wb"))

    def load_cookies(self, url):
        if not os.path.exists(self.cookie_path):
            print("No cookies found to load.")
            return

        cookies = pickle.load(open(self.cookie_path, "rb"))
        root_domain = self._get_root_domain(url)

        self.driver.get(url)  # Navigate to the domain first

        for cookie in cookies:
            # Only add the cookie if the domain matches
            if root_domain in cookie['domain']:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    print(f"Error adding cookie: {cookie}")
                    print(e)

#endregion


#region Local Storage
    def has_local_storage(self, url):
        if os.path.exists(self.local_storage_path):
            if os.path.getsize(self.local_storage_path) > 0:
                with open(self.local_storage_path, 'r') as file:
                    local_storage_data = json.load(file)
                
                # Parse the domain from the URL
                domain = urlparse(url).netloc

                # Check if there is any local storage data for the specified domain
                if domain in local_storage_data:
                    return True
        return False
    

    def save_local_storage(self):
        local_storage = self.driver.execute_script("return JSON.stringify(window.localStorage);")
        with open(self.local_storage_path, 'w') as file:
            file.write(local_storage)


    def load_local_storage(self, url):
        # Navigate to the provided URL
        self.driver.get(url)
        
        # Load local storage data from file and add them to the browser
        with open(self.local_storage_path, 'r') as file:
            data = file.read()
        self.driver.execute_script(f"window.localStorage = JSON.parse('{data}');")
#endregion


# region Example
if __name__ == '__main__':
    web_browser = WebBrowser()
    web_browser.driver.get("https://www.google.com")  # Test by opening Google
    web_browser.driver.quit()  # Close the browser after the test
#endregion