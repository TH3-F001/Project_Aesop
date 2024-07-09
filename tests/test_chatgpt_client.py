import unittest
from unittest.mock import patch, Mock
from src.infrastructure.api_clients.chatgpt_client import ChatGPTClient
from src.domain.models.chatgpt_requests import ChatGPTCompletionsRequest
from openai import OpenAI
from src.infrastructure.exceptions.openai_exceptions import *

from src.infrastructure.data_access.environment import Environment


class TestChatGPTClient(unittest.TestCase):
    def test_new_client_with_key(self):
        api_key = input("Please provide your OpenAI API Key:\n> ")
        result = ChatGPTClient.new_client(api_key)
        self.assertIsInstance(result, OpenAI)

    def test_new_client_without_key(self):
        Environment.load_environment()
        result = ChatGPTClient.new_client()
        self.assertIsInstance(result, OpenAI)

if __name__ == '__main__':
    unittest.main()
# class TestChatGPTClient(unittest.TestCase):
# def test_send_chat_message(api_key):
#     system_message="you are a punk rock song writer who writes parody lyrics with a modern punk rock twist to takes old-timey song titles"
#     user_message="Parody Daisy Bell by Harry Dacre"
#     request = ChatGPTCompletionsRequest(api_key, system_message, user_message)
#     return ChatGPTClient.send_chat_message(request)
#
#
# if __name__ == "__main__":
#     api_key = input("Provide your chatgpt API key:\n> ")
#     Environment.set_environment_variable("OPENAI_API_KEY", api_key)
#     Environment.load_environment()
#
#     print(test_send_chat_message(api_key))
