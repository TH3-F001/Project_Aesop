import requests
import json
import uuid
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from common.content_helper import Helper
'''
A class that utilizes the elevenlabs API for realistic text-to-speech conversion

Parameters: 
    cred_path: stores the api key in a flat json file
    voices_file: a json dictionary of voice names, and their voice_ids
'''
class Dictator:
    def __init__(self, cred_path, voices_path):
        # Load API Key
        creds = Helper.load_json(cred_path)
        # voicemap = Helper.load_json(voices_path)
        self.api_key = creds["api_key"]
        self.client = ElevenLabs(
            api_key=self.api_key
        )
        self.voices_path = voices_path
        self.voices = {}
        try:
            self.voices = Helper.load_json(voices_path)
        except json.JSONDecodeError:
            self.register_voices()

    def register_voices(self):
        voices = self.client.voices.get_all().json()
        print(type(voices))
        Helper.save_json_to_file(voices, self.voices_path)
        self.voices = voices

    def get_voice_id(self, voice_name: str) -> str:
        for voice in self.voices['voices']:
            if voice['name'].lower() == voice_name.lower():
                return voice['voice_id']
        raise ValueError(f"Voice: {voice_name} ID could not be found")

    def convert_text_to_speech(self, text, output_path, voice_name, model="eleven_turbo_v2", stability=0.0, similarity=1.0, style=0.0):
        voice_id = self.get_voice_id(voice_name)
        voice_settings = VoiceSettings(
            stability=stability,
            similarity_boost=similarity,
            style=style,
            use_speaker_boost=True)
        response = self.client.text_to_speech.convert(
            voice_id=voice_id,
            optimize_streaming_latency=0,
            output_format="mp3_44100_64",
            text=text,
            model_id=model,
            voice_settings=voice_settings
        )

        with open(output_path, "wb") as file:
            for chunk in response:
                if chunk:
                    file.write(chunk)
