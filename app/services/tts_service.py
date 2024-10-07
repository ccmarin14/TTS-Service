import json
from TTS.api import TTS

class TTSService:
    def __init__(self):
        # Cargar los modelos desde el archivo JSON
        with open("app/data/model.json", "r") as f:
            data = json.load(f)
            self.models = {model['id']: model for model in data['models']}

    def synthesize(self, text: str, model: int, output_path: str):
        model_data = self.models.get(model)
        if model_data is None:
            raise ValueError("Modelo no encontrado.")
        
        model_name = model_data['model']
        
        # Inicializar el modelo y generar el audio
        tts = TTS(model_name=model_name)
        tts.tts_to_file(text, file_path=output_path, speed=0.5, pitch=1.0)
