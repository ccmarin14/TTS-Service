import requests

from app.models.information_model import InformationModel
from .base_provider import TTSProvider

class VoicemakerProvider(TTSProvider):
    def build_request(self, text:str, model:InformationModel) -> dict:
        voice_id = model.model

        return {
            'url': self.config['url'],
            'headers': {
                "Content-Type": self.config['headers']['Content-Type'],
                "AUTHORIZATION": self.config['credentials']['AUTHORIZATION'],
            },
            'payload': {
                "Engine": self.config['defaults']['voice_engine'],
                "OutputFormat": self.config['defaults']['output_format'],
                "MasterSpeed": self.config['defaults']['speed'],
                "SampleRate": self.config['defaults']['rate'],
                "VoiceId": voice_id,
                "LanguageCode": model.language,
                "Text": text,
                "ResponseType": "stream"
            }
        }

    def execute_request(self, request: dict) -> bytes:
        response = requests.post(
            request['url'], 
            headers=request['headers'], 
            json=request['payload'], 
        )
        if response.status_code != 200:
            raise ValueError(f"Error al llamar a la API: {response.text}")
        return response