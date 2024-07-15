from typing import List
from src.domain.value_objects.scene_data import SceneData

class Script:
    """Standardized object that holds response data from an IScriptService implementer.
       A script holds data used to generate content like ImageClips, VideoClips, and AudioClips,
       as well as metadata for the end video like title, description tags, etc.
    """
    def __init__(self, title: str, description: str, tags: List[str], pinned_comment: str, scenes: List[SceneData]):
        self._title = title
        self._description = description
        self._tags = tags
        self._pinned_comment = pinned_comment
        self._scenes = scenes

    def __str__(self):
        scenes_str = '\n'.join([str(scene) for scene in self._scenes])
        return (f"Title: {self._title}\nDescription: {self._description}\nTags: {', '.join(self._tags)}\n"
                f"Pinned Comment: {self._pinned_comment}\nScenes:\n{scenes_str}")

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = value

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    @property
    def tags(self) -> List[str]:
        return self._tags

    @tags.setter
    def tags(self, value: List[str]):
        self._tags = value

    @property
    def pinned_comment(self) -> str:
        return self._pinned_comment

    @pinned_comment.setter
    def pinned_comment(self, value: str):
        self._pinned_comment = value

    def get_scenes(self) -> List[SceneData]:
        """Return all scenes."""
        return self._scenes

    def get_scene(self, name: str) -> SceneData:
        """Return a specific scene by name."""
        for scene in self._scenes:
            if scene.name == name:
                return scene
        raise ValueError('Scene not found')

    def get_scene_dialog(self, name: str) -> str:
        """Return the dialog of a specific scene by name."""
        scene = self.get_scene(name)
        return scene.dialog

    def get_scene_visual_prompt(self, name: str) -> str:
        """Return the visual prompt of a specific scene by name."""
        scene = self.get_scene(name)
        return scene.visual_prompt


