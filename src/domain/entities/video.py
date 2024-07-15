import datetime
from typing import Dict, List
from src.domain.entities.scene import Scene



class Video:
    title: str
    url: str
    description: str
    tags: List[str]
    pinned_comment: str
    scenes: List[Scene]
    script: Script
    image_prompts: Dict
    images: Dict
    transition_time: float
    scene_transitions: Dict
    length: str
    creation_date: datetime.datetime = field(default_factory=datetime.datetime.now)


    def __init__(self, title: str, description:str, tags: List[str], pinned_comment: str, url=''):
        self.title = title
        self.description = description
        self.tags = tags
        self.pinned_comment = pinned_comment
        self.url = url


