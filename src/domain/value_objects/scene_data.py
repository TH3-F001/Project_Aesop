class SceneData:
    def __init__(self, name: str, dialog: str, visual_prompt: str):
        self._name = name
        self._dialog = dialog
        self._visual_prompt = visual_prompt

    @property
    def name(self) -> str:
        """Get the name of the scene."""
        return self._name

    @name.setter
    def name(self, value: str):
        """Set the name of the scene. Ensure the name is not empty."""
        if not value:
            raise ValueError("Name cannot be empty.")
        self._name = value

    @property
    def dialog(self) -> str:
        """Get the dialog of the scene."""
        return self._dialog

    @dialog.setter
    def dialog(self, value: str):
        """Set the dialog of the scene. Ensure the dialog is not empty."""
        if not value:
            raise ValueError("Dialog cannot be empty.")
        self._dialog = value

    @property
    def visual_prompt(self) -> str:
        """Get the visual prompt of the scene."""
        return self._visual_prompt

    @visual_prompt.setter
    def visual_prompt(self, value: str):
        """Set the visual prompt of the scene. Ensure the visual prompt is not empty."""
        if not value:
            raise ValueError("Visual prompt cannot be empty.")
        self._visual_prompt = value
