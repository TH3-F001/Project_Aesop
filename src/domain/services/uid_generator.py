import uuid


class UIDGenerator:
    """A class that generates unique identifiers suitable for persistent storage."""
    @staticmethod
    def generate_uuid():
        """Returns a UUID string that can be used as a unique identifier."""
        return str(uuid.uuid4())


