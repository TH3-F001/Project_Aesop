from src.domain.models.chatgpt_requests import *
from src.infrastructure.exceptions.openai_exceptions import *
from openai import OpenAI, Model, OpenAIError
from time import sleep

class ChatGPTClient:

    @staticmethod
    def new_client(api_key="")-> OpenAI:
        if api_key != "":
            return OpenAI(api_key=api_key)
        return OpenAI()

    @staticmethod
    def send_chat_message(completions_request: ChatGPTCompletionsRequest):
        client = OpenAI()
        try:
            completion = client.chat.completions.create(
                model=completions_request.gpt_model,
                messages=completions_request.messages
            )
            finish_reason = completion.choices[0].finish_reason
            match finish_reason:
                case "stop":
                    return completion.choices[0].message
                case "length":
                    raise OpenAITokenLengthExceededException()
                case "content_filter":
                    raise OpenAIContentFilterException()
                case _:
                    raise OpenAIUnexpectedFinishReason(finish_reason)
        except Exception as e:
            print(e)




