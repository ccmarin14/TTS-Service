import boto3
from .base_provider import TTSProvider

class PollyProvider(TTSProvider):
    def __init__(self, config: dict):
        super().__init__(config)
        self.client = boto3.client(
            'polly',
            aws_access_key_id=config['access_key_id'],
            aws_secret_access_key=config['secret_access_key'],
            region_name=config['region']
        )

    #Código sin probar
    def build_request(self, text: str, voice_id: str) -> dict:
        return {
            'Text': text,
            'OutputFormat': 'mp3',
            'VoiceId': voice_id,
            'Engine': 'neural'
        }
    
    #Código sin probar
    def execute_request(self, response):
        return response['AudioStream'].read()