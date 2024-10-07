import hashlib
from pathlib import Path

class FileService:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)  # Crear directorio si no existe

    def generate_hash(self, text: str) -> str:
        """Generar un hash único basado en el texto."""
        clean_text = ''.join(e for e in text if e.isalnum() or e.isspace())  # Limpiar el texto
        return hashlib.md5(clean_text.encode('utf-8')).hexdigest()

    def get_audio_path(self, text: str) -> Path:
        """Obtener la ruta completa del archivo de audio basado en el hash."""
        text_hash = self.generate_hash(text)
        return self.output_dir / f"{text_hash}.wav"

    def audio_exists(self, text: str) -> bool:
        """Verificar si el archivo de audio ya existe."""
        return self.get_audio_path(text).exists()