from src.domain.entities.prompt import Prompt
from typing import Protocol, Dict


class IPromptService(Protocol):
    def generate_prompt(self, prompt_data: Dict) -> Prompt:
        raise NotImplementedError
