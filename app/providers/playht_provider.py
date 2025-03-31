import requests

from app.models.information_model import InformationModel
from .base_provider import TTSProvider

class PlayHTProvider(TTSProvider):
    def build_request(self, text: str, model:InformationModel) -> dict:
        voice_id = model.model

        return {
            'url': self.config['url'],
            'headers': {
                "Content-Type": self.config['headers']['Content-Type'],
                "X-USER-ID": self.config['credentials']['X-USER-ID'],
                "AUTHORIZATION": self.config['credentials']['AUTHORIZATION'],
                "accept": self.config['headers']['accept'],
            },
            'payload': {
                "voice_engine": self.config['defaults']['voice_engine'],
                "output_format": self.config['defaults']['output_format'],
                "speed": self.config['defaults']['speed'],
                "text": text,
                "voice": voice_id
            }
        }

    def execute_request(self, request: dict) -> bytes:
        response = requests.post(
            request['url'],
            json=request['payload'], 
            headers=request['headers'],
        )
        if response.status_code != 200:
            raise ValueError(f"Error al llamar a la API: {response.text}")
        return response