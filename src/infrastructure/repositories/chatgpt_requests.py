from typing import Dict


class ChatGPTCompletionsRequest:
    VALID_MODELS = [
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-0125",
        "gpt-3.5-turbo-0301",
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-1106",
        "gpt-3.5-turbo-16k",
        "gpt-3.5-turbo-16k-0613",
        "gpt-3.5-turbo-instruct",
        "gpt-3.5-turbo-instruct-0914",
        "gpt-4",
        "gpt-4-0125-preview",
        "gpt-4-0613",
        "gpt-4-1106-preview",
        "gpt-4-turbo",
        "gpt-4-turbo-2024-04-09",
        "gpt-4-turbo-preview",
        "gpt-4o",
        "gpt-4o-2024-05-13",
    ]
    def __init__(self, api_key: str, system_message: str, user_message:str, gpt_model="gpt-4-turbo-preview"):
        self.api_key = api_key
        self.gpt_model = gpt_model
        self.messages = []

        self.system_message = self.add_system_message(system_message)
        self.initial_user_message = self.add_user_message(user_message)

        self.validate_model()

    def validate_model(self):
        if self.gpt_model not in self.VALID_MODELS:
            raise ValueError(f"Invalid gpt_model '{self.gpt_model}'. Must be one of {', '.join(self.VALID_MODELS)}")

    def _add_message(self, message, role):
        valid_roles = ["assistant", "user", "system"]

        if role not in valid_roles:
            raise ValueError(f"Invalid role '{role}'. Must be one of {', '.join(valid_roles)}")

        message = {"role": role, "content": message}
        self.messages.append(message)
        return message


    def add_system_message(self, message) -> Dict:
        return self._add_message(message, "system")

    def add_assistant_message(self, message):
        return self._add_message(message, "assistant")

    def add_user_message(self, message):
        return self._add_message(message, "user")

    def free_message_history(self):
        messages = []
        self.add_system_message(self.system_message)


class ChatGPTDalleRequest:
    VALID_MODELS = [
        "dall-e-2",
        "dall-e-3",
    ]


class ChatGPTTextToSpeechRequest:
    VALID_MODELS = [
        "tts-1",
        "tts-1-hd",
    ]


class chatGPTAssistantRequest:
    VALID_MODELS = [
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-0125",
        "gpt-3.5-turbo-0301",
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-1106",
        "gpt-3.5-turbo-16k",
        "gpt-3.5-turbo-16k-0613",
        "gpt-3.5-turbo-instruct",
        "gpt-3.5-turbo-instruct-0914",
        "gpt-4",
        "gpt-4-0125-preview",
        "gpt-4-0613",
        "gpt-4-1106-preview",
        "gpt-4-turbo",
        "gpt-4-turbo-2024-04-09",
        "gpt-4-turbo-preview",
        "gpt-4o",
        "gpt-4o-2024-05-13",
    ]


