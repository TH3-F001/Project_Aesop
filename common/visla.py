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
        self.root_prompt_file = "appdata/visla_root_prompt.txt"

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


        print("\tLoaded.")
        

#region Navigation
    def sign_in(self):
        print("\tSigning in...")
        email = self.conf["creds"]["email"]
        pw = self.conf["creds"]["password"]

        email_field = self.browser.get_element("name", "email")
        password_field = self.browser.get_element("name", "password")

        self.browser.type_keys(email_field, email)
        self.browser.type_keys(password_field, pw)
        self.browser.type_enter(password_field)

        # Wait for the web page to load
        self.browser.get_element("id", "Create Video")

        # Click center of the web page to bypass tutorial dialog
        self.browser.click_center_screen()
        self.browser.save_cookies()


    def log_on(self):
        print("\nLogging on to visla.com...")
        self.browser.goto_url(self.home_url)
        if self.browser.has_cookies(self.home_url):
            self.browser.load_cookies(self.home_url)
            self.browser.goto_url(self.home_url)

        self.sign_in()


    def create_video(self):
        if not self.browser.get_current_url() == self.home_url:
            print("ERROR: You must log in to visla before creating a video")
            return None

        # Click the new video button
        print("Clicking 'Create a New Video...")
        create_video_btn = self.browser.get_element("id", "Create Video")
        self.browser.click(create_video_btn)

        # Type in root prompt
        print("Typing Root Prompt...")
        root_prompt = self.get_root_prompt()
        input_field = self.browser.get_element("xpath", "//textarea[@placeholder]")
        sleep(1)
        self.browser.type_keys(input_field, root_prompt)

        # Use Only Free Stock
        print("Clicking Generate Options Button...")
        generate_options_btn = self.browser.get_element("class_name", "visla-button-only-icon")
        self.browser.click(generate_options_btn)
        print("Clicking Premium Stock CheckBoxes...")

        #!TODO Checkboxes are not being generated properly!

        premium_stock_checkboxes = self.browser.get_elements("css_selector", "input[name='usePremiumStock']")
        print(premium_stock_checkboxes)
        for checkbox in premium_stock_checkboxes:
            self.browser.click(checkbox)
            print("CheckBox Clicked:", checkbox)
        self.browser.click_top_screen()

        # Generate Video
        print("Clicking Generate Video Button...")
        generate_btn = self.browser.get_element("class_name", "visla-button-primary")
        self.browser.click(generate_btn)

        # Wait for video to generate
        print("Waiting for Video to generate...")
        self.browser.wait_for_element(300, "tag_name", "canvas", )
        self.browser.click_top_screen()

        # Export video
        print("Exporting Video...")
        export_button = self.browser.get_element("class_name", "ug-export-video",)
        self.browser.click(export_button)

        sleep(1000)

        options_button = self.browser.get_element("xpath", "//*[name()='svg' and @xmlns='http://www.w3.org/2000/svg']")


    def open_homepage(self):
        self.browser.get(self.home_url)
        sleep(1)
#endregion


#region Utilities
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

    def get_root_prompt(self):
        with open(self.root_prompt_file, 'r') as file:
            root_prompt = file.read()

        return root_prompt
#endregion




        
