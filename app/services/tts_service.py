from TTS.api import TTS

class TTSService:
    def __init__(self):
        self.models = {
            0: "tts_models/en/jenny/jenny",  # Optimizado para voces naturales. Debilidad: Puede no ser tan versátil.
            1: "tts_models/en/ljspeech/tacotron2-DDC",  # Muy buena calidad de voz. Debilidad: Requiere más tiempo de entrenamiento.
            2: "tts_models/en/ljspeech/glow-tts",  # Eficiente y versátil. Debilidad: Calidad variable dependiendo de los datos.
            3: "tts_models/en/ljspeech/speedy-speech",  # Muy rápido en síntesis para textos largos. Debilidad: Puede sacrificar calidad.
            4: "tts_models/en/ljspeech/tacotron2-DCA",  # Mejora en prosodia y entonación, bueno para frases. Debilidad: Requiere más recursos computacionales.
            5: "tts_models/en/ljspeech/fast_pitch",  # Bueno y rápido. Debilidad: Limitado en variaciones de tono.
            20: "tts_models/es/mai/tacotron2-DDC",  # Excelente calidad en español. Debilidad: Menor disponibilidad de datos.
            21: "tts_models/es/css10/vits",  # Alto rendimiento en español. Debilidad: Puede ser complejo de ajustar.
        }

    def synthesize(self, text: str, model: int, output_path: str):
        model_name = self.models.get(model)
        if model_name is None:
            raise ValueError("Modelo no encontrado.")
        
        self.tts = TTS(model_name=model_name)

        self.tts.tts_to_file(text , file_path=output_path, speed=1.0, pitch=1.0)
