import json
from TTS.api import TTS

class TTSService:
    def __init__(self, file_service: 'FileService'):
        # Cargar los modelos desde el archivo JSON
        with open("app/data/model.json", "r") as f:
            data = json.load(f)
            self.models = {model['id']: model for model in data['models']}
        self.file_service = file_service
        
    def synthesize(self, text: str, model: int):
        # Limpiar espacios al inicio y al final
        text = text.strip()
        
        # Asegurarse de que el último carácter sea un punto
        if text and text[-1] != '.':
            text += '.'


        model_data = self.models.get(model)
        if model_data is None:
            raise ValueError("Modelo no encontrado.")
        
        model_name = model_data['model']

        audio_name = text + model_name

        # Generar el hash del texto
        audio_path = self.file_service.get_audio_path(audio_name)

        # Si el archivo ya existe, retornar la ruta
        if self.file_service.audio_exists(audio_name):
            return str(audio_path)
        
        # Inicializar el modelo y generar el audio
        tts = TTS(model_name=model_name)
        tts.tts_to_file(text, file_path=audio_path, speed=1.0, pitch=1.0)
        return str(audio_path)
