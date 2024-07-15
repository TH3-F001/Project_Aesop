from src.domain.enumerations import SceneTransitions
from src.domain.data_classes.audio_clip import AudioClip
from src.domain.data_classes.content import Content


class VideoClip(Content):
    """Holds simple information about a video clip with getters and setters"""
    def __init__(self, name: str, duration: float, dialog: str, audio: AudioClip, transition: SceneTransitions, video):
        super().__init__(name)
        self._duration = duration
        self._dialog = dialog
        self._video = video
        self._scene_transition = transition
        self._audio = audio

    @property
    def duration(self) -> float:
        """Get the duration of the video clip."""
        return self._duration

    @duration.setter
    def duration(self, value: float):
        """Set the duration of the video clip ensuring it is non-negative."""
        if value < 0:
            raise ValueError('Duration cannot be negative')
        self._duration = value

    @property
    def dialog(self) -> str:
        """Get the dialog associated with the video clip."""
        return self._dialog

    @dialog.setter
    def dialog(self, value: str):
        """Set the dialog associated with the video clip."""
        self._dialog = value

    @property
    def video(self):
        """Get the video content."""
        return self._video

    @video.setter
    def video(self, value):
        """Set the video content."""
        self._video = value

    @property
    def scene_transition(self) -> SceneTransitions:
        """Get the scene transition used in the video clip."""
        return self._scene_transition

    @scene_transition.setter
    def scene_transition(self, value: SceneTransitions):
        """Set the scene transition used in the video clip."""
        self._scene_transition = value

    @property
    def audio(self) -> AudioClip:
        """Get the audio clip associated with the video clip."""
        return self._audio

    @audio.setter
    def audio(self, value: AudioClip):
        """Set the audio clip associated with the video clip."""
        self._audio = value

