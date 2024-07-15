from typing import List, Dict


class Prompt:
    """Represents a prompt with instructions, example script, and channel data."""
    def __init__(self, role: str, instructions: List[str], example_script: Dict, example_channel_data: Dict, max_word_count: int):
        self._role = role
        self._instructions = instructions
        self._example_script = example_script
        self._example_channel_data = example_channel_data
        self._max_word_count = max_word_count

    @property
    def role(self) -> str:
        """Get the role of the prompt."""
        return self._role

    @role.setter
    def role(self, value: str):
        """Set the role of the prompt."""
        self._role = value

    @property
    def instructions(self) -> List[str]:
        """Get the list of instructions."""
        return self._instructions

    @instructions.setter
    def instructions(self, value: List[str]):
        """Set the list of instructions."""
        self._instructions = value

    @property
    def example_script(self) -> dict:
        """Get the example script."""
        return self._example_script

    @example_script.setter
    def example_script(self, value: dict):
        """Set the example script."""
        self._example_script = value

    @property
    def example_channel_data(self) -> dict:
        """Get the example channel data."""
        return self._example_channel_data

    @example_channel_data.setter
    def example_channel_data(self, value: dict):
        """Set the example channel data."""
        self._example_channel_data = value

    @property
    def max_word_count(self) -> int:
        """Get the maximum word count."""
        return self._max_word_count

    @max_word_count.setter
    def max_word_count(self, value: int):
        """Set the maximum word count."""
        self._max_word_count = value
