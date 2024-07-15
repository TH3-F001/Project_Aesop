from typing import Protocol


class ICredential(Protocol):
    def get_auth_data(self) -> dict:
        """Returns the appropriate authentication data for a given implementation"""
        raise NotImplementedError
