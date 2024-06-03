from common.browser import WebBrowser

from time import sleep
from pathlib import Path
import yaml
import os


class Visla:
    def __init__(self):
        self.home_url = "https://app.visla.us/home"
        self.login_url = "https://app.visla.us/signin"
        self.browser = WebBrowser(10)
        self.generation_wait_time = 500
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
        print("\tDone.")


    def create_video(self):
        if not self.browser.get_current_url() == self.home_url:
            print("ERROR: You must log in to visla before creating a video")
            return None

        # Click the new video button
        print("\nClicking 'Create a New Video...")
        create_video_btn = self.browser.get_element("id", "Create Video")
        self.browser.click(create_video_btn)
        print("\tDone.")

        # Type in root prompt
        print("\nTyping Root Prompt...")
        root_prompt = self.get_root_prompt()
        input_field = self.browser.get_element("xpath", "//textarea[@placeholder]")
        sleep(0.2)
        self.browser.type_keys(input_field, root_prompt)
        print("\tDone")

        # Deselect Premium Stock Assets (Free Stock Only)
        print("\nDeselecting Premium Stock Assets...")
        print("\tClicking Generate Options Button...")
        generate_options_btn = self.browser.get_element("class_name", "NN5VjCOHotdC")
        self.browser.click(generate_options_btn)
        print("\t\tClicked.")

        print("\tClicking Premium Footage CheckBox...")
        premium_footage_checkbox = self.browser.get_element("css_selector", "input[name='usePremiumStock']")
        self.browser.click(premium_footage_checkbox)
        print("\t\tDone.")

        print("\tClicking Premium BGM Button...")
        premium_bgm_checkbox = self.browser.get_element("css_selector", "input[name='usePremiumBgm']")
        self.browser.click(premium_bgm_checkbox)
        print("\t\tDone.")
        print("\tDone.")
        self.browser.click_top_screen()

        # Generate Video
        print("\nClicking Generate Video Button...")
        generate_btn = self.browser.get_element("class_name", "visla-button-primary")
        self.browser.click(generate_btn)
        print("\tDone.")

        # Wait for Video to Generate
        print("\nWaiting for Video to generate...")
        self.browser.wait_for_element(self.generation_wait_time, "tag_name", "canvas", )
        self.browser.click_top_screen()
        print("\tDone")

        # Export Video
        print("\nClicking Export Button...")
        export_btn = self.browser.get_element("css_selector", "span.ug-export-video button.visla-button-primary")
        self.browser.click(export_btn)
        print("\tDone")

        print("\nGrabbing Video Title...")
        sleep(3)
        title_element = self.browser.get_element("class_name", "b2vPNOl8zrMK")
        title = title_element.get_attribute("title")
        print("\tTitle:", title)
        print("\tDone.")

        # Wait for Video to Render (using the video element's presence as a trigger)
        print("\nWaiting for Video to Render...")
        share_btn_path = self.browser.wait_for_element(self.generation_wait_time, "class_name", "visla-player")
        print("\tDone.")

        print("\nClicking Video Options Button...")
        video_options_btn = self.browser.get_element("xpath", "(//div[@class='w9acVRfpV0Ap'])[4]")
        self.browser.click(video_options_btn)
        print("\tDone.")

        # print("\nFinding Download Button's Parent...")
        # parent_div = self.browser.get_element("css_selector", "div.i580RRW7epzK")
        # print("\tDone.")

        print("\nClicking Download Button...")
        download_btn = self.browser.get_element("xpath", "(//div[@class='ESbCbkij3jTe'])[3]")
        self.browser.click(download_btn)
        print("\tDone.")

        print("\nFinding Video In Downloads Folder...")
        downloads_dir = Path.home() / "Downloads"
        print("\tDownloads Directory:", downloads_dir)
        video_filename = f"{title}.mp4"
        video_filepath = downloads_dir / video_filename
        if not video_filepath.exists():
            print("\tERROR: Cannot find downloaded video")
            return None
        print("\tVideo Downloaded To:", video_filepath)
        print("\tDone.")





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




        
