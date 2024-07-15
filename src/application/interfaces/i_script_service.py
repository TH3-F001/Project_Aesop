from src.domain.entities.script import Script
from src.domain.entities.prompt import Prompt
from typing import Protocol


class IScriptService(Protocol):
    def generate_script(self, prompt: Prompt) -> Script:
        raise NotImplementedError
