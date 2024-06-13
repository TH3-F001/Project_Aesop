from openai import OpenAI
import os
import yaml


class ChatGPT:

    def __init__(self):
        config_path = "appdata/restricted/gpt.yaml"
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
        self.api_key = config["creds"]["api_key"]
        os.environ["OPENAI_API_KEY"] = self.api_key

        self.text_model = "gpt-3.5-turbo"

        video_gen_prompt_path = "appdata/prompts/gpt_videogen_prompt.txt"
        with open(video_gen_prompt_path, "r") as file:
            self.video_generator_prompt = file.read()

        self.client = OpenAI()

    def request_video_prompt(self):
        completion = self.client.chat.completions.create(
            model=self.text_model,
            messages=[
                {"role": "system",
                 "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
                {"role": "user", "content": f"{self.video_generator_prompt}"}
            ]
        )
        print(completion.choices[0].message)