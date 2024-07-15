from src.domain.services.uid_generator import UIDGenerator


class Content:
    """Defines common properties for different content clip sub-classes like audio clip, image clip and video clip"""
    def __init__(self, name):
        self._name = name
        self._id = UIDGenerator.generate_uuid()

    @property
    def name(self) -> str:
        """Getter for the name of the clip."""
        return self._name

    @name.setter
    def name(self, value: str):
        """Setter for the name of the clip."""
        self._name = value

    @property
    def id(self) -> str:
        """Getter for the id of the clip."""
        return self._id

    @id.setter
    def id(self, value: str):
        """Setter for the id of the clip."""
        self._id = value
