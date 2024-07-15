from src.application.interfaces.i_prompt_service import IPromptService
from src.domain.entities.prompt import Prompt
from src.domain.services.json_converter import JsonConverter
from typing import Dict

class ChatGptPromptService(IPromptService):
    def generate_prompt(self, prompt_data: Dict) -> Prompt:
        required_data = [
            'role',
            'instructions',
            'example_script',
            'channel_data',
            'max_word_count',
        ]
