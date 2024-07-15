from typing import Dict
from src.domain.entities.prompt import Prompt
from src.application.interfaces.i_prompt_service import IPromptService


class GeneratePrompt:
    def __int__(self, prompt_service:IPromptService):
        self.prompt_service = prompt_service

    def execute(self, prompt_data: Dict) -> Prompt:
        return self.prompt_service.generate_prompt(prompt_data)
