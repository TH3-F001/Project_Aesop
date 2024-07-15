from src.domain.interfaces.i_email_validator import IEmailValidator


class Email:
    """Stores email addresses and validates them with an email validator"""

    def __init__(self, address: str, validator: IEmailValidator):
        self._validator = validator
        self.address = address

    @property
    def address(self) -> str:
        """The getter for the email address."""
        return self._address

    @address.setter
    def address(self, value: str):
        """The setter for the email address that includes validation."""
        value = value.lower()
        if not self._validator.validate(value):
            raise ValueError(f'Email address is invalid: {value}')
        self._address = value

