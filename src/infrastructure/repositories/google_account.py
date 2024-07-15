from typing import List
from src.domain.value_objects.email import Email
from src.domain.services.quota_manager import QuotaManager
from src.domain.entities.youtube_channel import YoutubeChannel
from src.domain.exceptions.core_exceptions import MissingArgumentException
from src.domain.entities.google_api_credential import GoogleApiCredential





class GoogleAccount:
    _email: Email
    _youtube_quota_manager: QuotaManager
    _credentials: GoogleApiCredential
    _channels = List[YoutubeChannel]

    def __init__(self, email: Email, credentials: GoogleApiCredential, quota_manager: QuotaManager):
        if not client_id:
            raise MissingArgumentException('client_id')
        if not client_secret:
            raise MissingArgumentException('client_secret')

        if spent_quota < 0:
            spent_quota = 0

        self._email = email
        self.__spent_quota = spent_quota
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__MAX_QUOTA = max_quota


#region Getters
    def get_spent_quota(self) -> int:
        return self.__spent_quota

    def get_max_quota(self) -> int:
        return self.__MAX_QUOTA

    def get_email(self) -> str:
        return self._email

    def get_client_id(self) -> str:
        return self.__client_id

    def get_client_secret(self) -> str:
        return self.__client_secret
#endregion

    def spend_quota(self, quota_cost: int):
        if quota_cost < 0:
            raise ValueError(f"spend_quota's quota_cost arg must be a positive number, instead got {quota_cost}")
        if (quota_cost + self.__spent_quota) > self.__MAX_QUOTA:
            raise ValueError(f"{self._email} has insufficient quota to perform this action: {self.__spent_quota}/{self.__MAX_QUOTA}")
        self.__spent_quota += quota_cost

    def reset_quota(self):
        self.__spent_quota = 0

    def set_email(self, email):
        if self._email and Email.email_is_valid(self._email):
            raise ValueError("Google account emails may only be changed once.")

        if not Email.email_is_valid(email):
            raise ValueError(f"Input email does not match valid email format: {email}")

        self._email = email
