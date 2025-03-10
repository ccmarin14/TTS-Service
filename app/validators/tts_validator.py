import re
from app.models.tts_model import (
    TextToSpeechRequestById,
    TextToSpeechRequestByName,
    TextToSpeechRequestOptional,
    Gender,
    VoiceType
)

class TTSValidator:
    """Clase para validar las solicitudes de TTS"""
    
    @staticmethod
    def validate_base_request(request: TextToSpeechRequestById) -> None:
        """Valida los campos base de todas las solicitudes"""
        if not request.text or not request.text.strip():
            raise ValueError('El campo texto no puede estar vacío')
        if not request.read or not request.read.strip():
            raise ValueError('El campo lectura no puede estar vacío')

    @staticmethod
    def validate_language(language: str) -> None:
        """Valida el formato del lenguaje"""
        if not language or not re.match(r'^[a-z]{2}-[A-Z]{2}$', language):
            raise ValueError('El lenguaje debe tener el formato "xx-YY" (ej: "es-ES", "en-US")')
        
    @classmethod
    def validate_request_by_id(cls, request: TextToSpeechRequestById) -> None:
        """Valida una solicitud por el id de un modelo"""
        cls.validate_base_request(request)

    @classmethod
    def validate_request_by_name(cls, request: TextToSpeechRequestByName) -> None:
        """Valida una solicitud por nombre"""
        cls.validate_base_request(request)
        cls.validate_language(request.language)
        if not request.model or not request.model.strip():
            raise ValueError('El nombre del modelo es requerido')
        
    @classmethod
    def validate_request_optional(cls, request: TextToSpeechRequestOptional) -> None:
        """Valida una solicitud por nombre"""
        cls.validate_base_request(request)
        cls.validate_language(request.language)