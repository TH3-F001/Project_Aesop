class ChannelPromptData:
    """Represents a channel prompt that encapsulates various descriptive elements."""
    def __init__(self, name: str, focus: str, mission: str, background: str, mood: str):
        self._name = name
        self._focus = focus
        self._mission = mission
        self._background = background
        self._mood = mood

    @property
    def name(self) -> str:
        """Get the name of the channel."""
        return self._name

    @name.setter
    def name(self, value: str):
        """Set the name of the channel."""
        self._name = value

    @property
    def focus(self) -> str:
        """Get the focus of the channel."""
        return self._focus

    @focus.setter
    def focus(self, value: str):
        """Set the focus of the channel."""
        self._focus = value

    @property
    def mission(self) -> str:
        """Get the channel's mission."""
        return self._mission

    @mission.setter
    def mission(self, value: str):
        """Set channel's mission."""
        self._mission = value

    @property
    def background(self) -> str:
        """Get the background story of the channel"""
        return self._background

    @background.setter
    def background(self, value: str):
        """Set the background story of the channel"""
        self._background = value

    @property
    def mood(self) -> str:
        """Get the mood of the channel"""
        return self._mood

    @mood.setter
    def mood(self, value: str):
        """Set the mood of the channel."""
        self._mood = value
