import json
from TTS.api import TTS

class TTSService:
    def __init__(self):
        # Cargar los modelos desde el archivo JSON
        with open("app/data/model.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            self.models = {model['id']: model for model in data['models']}

    def synthesize(self, text: str, model: int, output_path: str):
        model_data = self.models.get(model)
        if model_data is None:
            raise ValueError("Modelo no encontrado.")
        
        model_name = model_data['model']
        
        # Asegurarse de que el texto esté en UTF-8
        print(repr(text))
        text = text.encode('utf-8', 'replace').decode('utf-8')

        # Inicializar el modelo y generar el audio
        tts = TTS(model_name=model_name)
        tts.tts_to_file(text, file_path=output_path, speed=1.0, pitch=1.0)

