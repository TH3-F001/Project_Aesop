from typing import Dict
from src.domain.enumerations import YoutubeActions

class GoogleAccount:
    __MAX_QUOTA = 10_000


    def __init__(self, args: dict):
        self.__email = args['email']
        self.__client_id = args['client_id']
        self.__client_secret = args['client_secret']
        self.__current_quota = args['spent_quota']

    def get_quota(self) -> int:
        return self.__current_quota

    def get_max_quota(self) -> int:
        return self.__MAX_QUOTA

    def get_email(self) -> str:
        return self.__email

    def get_client_id(self) -> str:
        return self.__client_id

    def get_client_secret(self) -> str:
        return self.__client_secret



    def spend_quota(self, action: YoutubeActions):
        if (action.value + self.__current_quota) > self.__MAX_QUOTA:
            raise ValueError(f"{self.__email} has insufficient quota to perform action: {action}")
        self.__current_quota += action.value

    def reset_quota(self):
        self.__current_quota = 0


