class Account:
    def __init__(self, id: str, name: str, credentials: dict):
        self._id = id
        self._name = name
        self._credentials = credentials

    @property
    def id(self) -> str:
        """Getter for the account ID."""
        return self._id

    @id.setter
    def id(self, value: str):
        """Setter for the account ID."""
        self._id = value

    @property
    def name(self) -> str:
        """Getter for the account name."""
        return self._name

    @name.setter
    def name(self, value: str):
        """Setter for the account name."""
        self._name = value

    @property
    def credentials(self) -> dict:
        """Getter for the account credentials."""
        return self._credentials

    @credentials.setter
    def credentials(self, value: dict):
        """Setter for the account credentials. Validates that the input is a dictionary."""
        if not isinstance(value, dict):
            raise ValueError('Credentials must be a dictionary.')
        self._credentials = value
