from typing import Dict

import requests
import re
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
import os
import json
from pathlib import Path
import shutil

class Helper():
    @staticmethod
    def download_image(url: str, destination_path: str):
        try:
            # GET the image url and check for error status codes
            response = requests.get(url)
            response.raise_for_status()
            
            # Convert response to a binary image
            image = Image.open(BytesIO(response.content))

            # save the image to destination
            image.save(destination_path)
            print(f"\tImage successfully downloaded and saved to {destination_path}")
        except requests.exceptions.RequestException as e:
            print(f"\tError downloading the image: {e}")
        except IOError as e:
            print(f"\tError saving the image: {e}")

    @staticmethod
    def get_web_page(url, return_type="text"):
        try:
            response = requests.get(url)
            response.raise_for_status()

            match return_type:
                case "html":
                    return response.content
                case "text":
                    soup = BeautifulSoup(response.content, 'html.parser')
                    text = soup.get_text(separator=' ', strip=True)
                    # Remove extra whitespace and newlines
                    text = re.sub(r'\s+', ' ', text)
                    return text
                case _:
                    raise ValueError("Invalid return type specified")
        except requests.RequestException as e:
            print(f"Error fetching the URL: {e}")
            return None

    @staticmethod
    def make_string_filesafe(file_name: str) -> str:
        safe_name = re.sub(r'[\\/*?:"<>| ]', '_', file_name)
        return safe_name

        # Example usage
        unsafe_name = "My:Invalid/File*Name?.txt"
        safe_name = make_file_safe(unsafe_name)
        print(safe_name)  # Output: My_Invalid_File_Name_.txt

    @staticmethod
    def create_directory_structure(target_dir_path):
        os.makedirs(target_dir_path, exist_ok=True)

    @staticmethod
    def move_file(source_file: str, destination_folder: str):
        Helper.create_directory_structure(destination_folder)
        shutil.move(source_file, destination_folder)

    @staticmethod
    def convert_string_to_json(json_string):
        clean_json_string = json_string.replace("```json", '').replace("```", '')
        return json.loads(clean_json_string)

    @staticmethod
    def load_json(filepath: str) -> Dict:
        try:
            with open(filepath, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: The file '{filepath}' does not exist.")
        except json.JSONDecodeError:
            raise json.JSONDecodeError(f"Error: The file '{filepath}' contains invalid JSON.")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}")

    @staticmethod
    def save_json_to_file(json_data, file_path):
        try:
            # If json_data is a string, parse it into a dictionary
            if isinstance(json_data, str):
                json_data = json.loads(json_data)

            # Save the dictionary as a JSON file
            with open(file_path, 'w') as file:
                json.dump(json_data, file, indent=4)

            print(f"JSON data successfully saved to {file_path}")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON string: {e}")
        except IOError as e:
            print(f"Error writing JSON to file: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    @staticmethod
    def get_parent_directory(filepath: str) -> str:
        path_obj = Path(filepath)
        parent_directory = path_obj.parent
        return str(parent_directory)

