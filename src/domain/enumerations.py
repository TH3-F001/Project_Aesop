from enum import Enum, auto


class ChannelMoods(Enum):
    MYSTERIOUS = 'Mysterious'
    HIGH_ENERGY = 'High Energy'
    HUMOROUS = 'Humorous'
    SCANDALOUS = 'Scandalous'
    FEAR_MONGERING = 'Fear Mongering'
    ANGER_INDUCING = 'Anger Inducing'


class SceneTransitions(Enum):
    FADE_IN = auto()
    FADE_OUT = auto()
    CROSS_FADE = auto()
    HARD_CUT = auto()
    SLIDE_UP = auto()
    SLIDE_DOWN = auto()
    SLIDE_LEFT = auto()
    SLIDE_RIGHT = auto()
