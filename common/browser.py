from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import json
import os

class WebBrowser:
    def __init__(self):
        # Set Filepaths:
        self.geckodriver_path = 'appdata/geckodriver'
        self.cookie_path = 'appdata/cookies.json'
        self.local_storage_path = 'appdata/local_storage.json'
        self.sessions_path = 'appdata/sessions.json'

        # Initialize the Options object
        self.options = Options()
        # self.options.headless = True
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
        
        # Initialize the Service Object
        self.service = Service(executable_path=self.geckodriver_path)

        # Initialize the WebDriver with the specified options
        self.driver = webdriver.Firefox(options=self.options, service=self.service)

        # Load cache and cookies if avaliable:
        if self.has_cookies:
            print("has_cookies")
            # self.load_cookies()
        if self.has_local_storage:
            print("has_stragage")
            # self.load_local_storage()
        



    def get(self, url=""):
        if url != "":
            try:
                result = self.driver.get(url)
            except:
                print("Invalid URL! Try again!")
                return
            return result


    def has_cookies(self):
        if os.path.exists(self.cookie_path):
            if (os.path.getsize(self.cookie_path) > 0):
                return True
        return False


    def has_local_storage(self):
        if os.path.exists(self.local_storage_path):
            if (os.path.getsize(self.local_storage_path) > 0):
                return True
        return False


    def save_cookies(self):
        cookies = self.driver.get_cookies()
        with open(self.cookie_path, 'w') as file:
            json.dump(cookies, file)

    
    def save_local_storage(self):
        local_storage = self.driver.execute_script("return JSON.stringify(window.localStorage);")
        with open(self.local_storage_path, 'w') as file:
            file.write(local_storage)


    def load_cookies(self):
        with open(self.cookie_path, 'r') as file:
            cookies = json.load(file)

        for cookie in cookies:
            self.driver.add_cookie(cookie)


    def load_local_storage(self):
        with open(self.local_storage_path, 'r') as file:
            data = file.read()
        self.driver.execute_script(f"window.localStorage = JSON.parse('{data}');")


    def save_and_close(self):
        self.save_local_storage
        self.save_cookies
        self.driver.quit

# Example of using the class
if __name__ == '__main__':
    web_browser = WebBrowser()
    web_browser.driver.get("https://www.google.com")  # Test by opening Google
    web_browser.driver.quit()  # Close the browser after the test
