from src.domain.enumerations import SceneTransitions
from typing import Dict


class Scene:
    def __init__(self, args: Dict):
        self.name: str
        self.exit_transition: SceneTransitions