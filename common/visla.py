from common.browser import WebBrowser

from time import sleep

import yaml
import os


class Visla:
    def __init__(self):
        self.home_url = "https://app.visla.us/home"
        self.login_url = "https://app.visla.us/signin"
        self.browser = WebBrowser(10)
        conf_file = "appdata/visla.yaml"

        # Create visla config file if it doesnt already exist
        if not os.path.exists(conf_file):
            self.create_config_file(conf_file)

        # Load visla config file into self.conf
        print("\nLoading visla.yaml...")
        with open(conf_file, 'r') as file:
            self.conf = yaml.safe_load(file)
        print("\t Loaded.")

        # Create Browser Object
        print("\nGenerating WebBrowser...")
        self.browser = WebBrowser(10)
        print("\tGenerated.")
        
        # Load Root Prompt file into self.root_prompt
        print("\nLoading visla_root_prompt.txt...")
        root_prompt_file = "appdata/visla_root_prompt.txt"
        with open(root_prompt_file, 'r') as file:
            self.root_prompt = yaml.safe_load(file)
        print("\tLoaded.")
        


    def create_config_file(self, path):
        print("\nConfig file not found. Please enter your credentials.")
        email = input("Enter your email: ")
        password = input("Enter your password: ")

        # Create a dictionary for the configuration
        conf = {
            'creds': {
                'email': email,
                'password': password
            }
        }

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'w') as file:
            yaml.dump(conf, file)
        
        print("\tConfiguration Complete.")


    def cookieless_login(self):
        print("\tSigning in...")
        email = self.conf["creds"]["email"]
        pw = self.conf["creds"]["password"]

        email_field = self.browser.get_element("name", "email")
        password_field = self.browser.get_element("name", "password")

        self.browser.type_keys(email_field, email)
        self.browser.type_keys(password_field, pw)
        self.browser.type_enter(password_field)

        create_vid_btn = self.browser.get_element("id", "Create Video")
        sleep(5)
        self.browser.save_cookies()


    def log_on(self):
        print("\nLogging on to visla.com...")
        self.browser.goto_url(self.home_url)
        if self.browser.has_cookies(self.home_url):
            self.browser.load_cookies()
            print(self.browser.driver.get_cookies())
        else:
            self.cookieless_login()
        # if self.browser.has_cookies(self.home_url):  
        # #     self.browser.load_cookies(self.login_url)
        # else:
        
            
            # if create_vid_btn:
                



            # sleep(5)

            # self.browser.save_cookies()
            # self.browser.save_local_storage()


    def open_homepage(self):
        self.browser.get(self.home_url)
        sleep(1)
        
