from abc import ABC, abstractmethod
from typing import Dict, Any

class TTSProvider(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    def build_request(self, text: str, voice_id: str) -> Dict[str, Any]:
        """Construye la solicitud específica del proveedor"""
        pass

    @abstractmethod
    def process_response(self, response: Any) -> bytes:
        """Procesa la respuesta del proveedor"""
        pass