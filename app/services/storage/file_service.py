import hashlib
from pathlib import Path

class FileService:
    """
    Clase para manejar la generación, almacenamiento y verificación de archivos de audio.

    Esta clase proporciona métodos para generar un hash único basado en el texto, 
    obtener la ruta completa de un archivo de audio en base al hash, y verificar si 
    dicho archivo ya existe en el sistema de archivos.
    """
        
    def __init__(self, output_dir: str):
        """
        Inicializa la clase FileService.
        Crea un directorio de salida donde se almacenarán los archivos de audio, si no existe.
        Args:
            output_dir (str): La ruta al directorio donde se almacenarán los archivos de audio.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)  # Crear directorio si no existe

    @staticmethod
    def generate_hash(text: str) -> str:
        """
        Genera un hash único basado en el texto proporcionado.

        El texto es limpiado para eliminar caracteres no alfanuméricos, excepto los espacios, 
        y luego se utiliza el algoritmo MD5 para generar un hash único.
        Args:
            text (str): El texto que se usará para generar el hash.
        Returns:
            str: El hash MD5 del texto limpio.
        """
        clean_text = ''.join(e for e in text if e.isalnum() or e.isspace())  # Limpiar el texto
        return hashlib.md5(clean_text.encode('utf-8')).hexdigest()

    def get_audio_path(self, text: str) -> Path:
        """
        Obtiene la ruta completa del archivo de audio basado en el hash del texto.

        El nombre del archivo será el hash MD5 del texto con la extensión `.mp3`.
        Args:
            text (str): El texto base para generar el nombre del archivo de audio.
        Returns:
            Path: La ruta completa del archivo de audio.
        """
        text_hash = self.generate_hash(text)
        return self.output_dir / f"{text_hash}.mp3"