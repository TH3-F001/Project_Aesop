from src.domain.data_classes.content import Content


class ImageClip(Content):
    """Holds simple information about an image clip with getters and setters"""
    def __init__(self, name: str, image):
        super().__init__(name)
        self._image = image

    @property
    def image(self):
        """Getter for the image data."""
        return self._image

    @image.setter
    def image(self, value):
        """Setter for the image data."""
        self._image = value
