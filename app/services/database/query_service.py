from typing import Dict, List
from app.models.information_model import information_model
from collections import defaultdict

class QueryService:
    """Servicio para organizar y estructurar resultados de consultas SQL"""

    @staticmethod
    def organize_voice_models(voices: List[information_model]) -> Dict:
        """
        Organiza los modelos de voz jerárquicamente por platform -> language -> type -> gender
        
        Args:
            voices (List[information_model]): Lista de modelos de voz

        Returns:
            Dict: Estructura jerárquica organizada de los modelos
        """
        organized_voices = defaultdict(
            lambda: defaultdict(
                lambda: defaultdict(
                    lambda: defaultdict(list)
                )
            )
        )

        for voice in voices:
            # Creamos un diccionario con solo los campos que no se usan para agrupar
            voice_fields = {
                field: getattr(voice, field)
                for field in vars(voice)
                if field not in ['platform', 'language', 'type', 'gender']
            }
            organized_voices[voice.platform][voice.language][voice.type][voice.gender].append(voice_fields)

        return organized_voices