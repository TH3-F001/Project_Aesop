from typing import Dict, List
from src.domain.enumerations import SceneTransitions

class Video:
    title: str
    url: str
    description: str
    tags: List[str]
    pinned_comment: str
    scenes: List[str]
    script: Dict
    image_prompts: Dict
    images: Dict
    transition_time: float
    scene_transitions: Dict
    length: str

    def __init__(self, args: Dict):
        ...


