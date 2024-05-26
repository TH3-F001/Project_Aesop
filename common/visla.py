from common.browser import WebBrowser

from time import sleep

import yaml
import os


class Visla:
    def __init__(self):
        self.home_url = "https://app.visla.us/home"
        self.login_url = "https://app.visla.us/signin"
        self.browser = WebBrowser(10)
        
        # Create visla config file if it doesnt already exist
        conf_file = "appdata/visla.yaml"
        if not os.path.exists(conf_file):
            self.create_config_file()

        # Load visla config file into self.conf
        with open(conf_file, 'r') as file:
            self.conf = yaml.safe_load(file)
        self.browser = WebBrowser(10)
        
        # Load Root Prompt file into self.root_prompt
        root_prompt_file = "appdata/visla_root_prompt.txt"
        with open(root_prompt_file, 'r') as file:
            self.root_prompt = yaml.safe_load(file)
        


    def create_config_file(self):
        print("Config file not found. Please enter your credentials.")
        email = input("Enter your email: ")
        password = input("Enter your password: ")

        # Create a dictionary for the configuration
        conf = {
            'creds': {
                'email': email,
                'password': password
            }
        }


    def login(self):
        print("going to ", self.home_url)
        self.browser.get(self.home_url)
        if self.browser.has_cookies(self.home_url):  
            self.browser.load_cookies(self.login_url)
        else:
            print("Logging in to Visla...")
            email = self.conf["creds"]["email"]
            pw = self.conf["creds"]["password"]

            email_field = self.browser.get_element("name", "email")
            password_field = self.browser.get_element("name", "password")

            self.browser.type_keys(email_field, email)
            self.browser.type_keys(password_field, pw)
            self.browser.type_enter(password_field)

            create_vid_btn = self.browser.get_element("id", "Create Video")
            
            # if create_vid_btn:
                



            # sleep(5)

            # self.browser.save_cookies()
            # self.browser.save_local_storage()


    def open_homepage(self):
        self.browser.get(self.home_url)
        sleep(1)
        
