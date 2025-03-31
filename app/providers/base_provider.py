from abc import ABC, abstractmethod
from typing import Dict, Any

from app.models.information_model import InformationModel

class TTSProvider(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    def build_request(self, text: str, model: InformationModel) -> Dict[str, Any]:
        """Construye la solicitud específica del proveedor"""
        pass

    @abstractmethod
    def execute_request(self, request: Dict[str, Any]) -> bytes:
        """Ejecuta la solicitud y retorna el audio en bytes"""
        pass