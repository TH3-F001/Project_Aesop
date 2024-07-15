from src.domain.data_classes.content import Content


class AudioClip(Content):
    """Holds simple information about an audio clip with getters and setters"""
    def __init__(self, name: str, duration: float, audio):
        super().__init__(name)
        self._duration = duration
        self._audio = audio

    @property
    def duration(self) -> float:
        """Getter for the duration of the audio clip."""
        return self._duration

    @duration.setter
    def duration(self, value: float):
        """Setter for the duration of the audio clip, ensuring it is a non-negative number."""
        if value < 0:
            raise ValueError('Duration cannot be negative')
        self._duration = value

    @property
    def audio(self):
        """Getter for the audio data."""
        return self._audio

    @audio.setter
    def audio(self, value):
        """Setter for the audio data."""
        self._audio = value
