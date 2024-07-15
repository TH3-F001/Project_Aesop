from typing import Protocol


class IUriValidator(Protocol):
    @staticmethod
    def validate(value: str) -> bool:
        """Validate a given value, return true if valid else, false"""
        raise NotImplementedError
