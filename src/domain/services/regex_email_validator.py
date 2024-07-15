from src.domain.interfaces.i_email_validator import IEmailValidator
from re import match


class RegexEmailEmailValidator(IEmailValidator):
    """Validates basic ascii emails using REGEX"""
    @staticmethod
    def validate(email_address: str) -> bool:
        """Validates email. Returns true if valid, else false"""
        max_chars = 254
        min_chars = 6

        if len(email_address) > max_chars or len(email_address) < min_chars:
            return False

        pattern = r'^[a-zA-Z0-9._%+-]+@(?![.-])[a-zA-Z0-9.-]+(?<![-.])\.[a-zA-Z]{2,}$'
        return bool(match(pattern, email_address))
