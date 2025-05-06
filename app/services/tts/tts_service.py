import os
from typing import Dict
import requests
from app.models.information_model import InformationModel
from app.models.tts_model import TextToSpeechRequestById
from app.providers.playht_provider import PlayHTProvider
from app.providers.polly_provider import PollyProvider
from app.providers.voicemaker_provider import VoicemakerProvider
from app.services.container_service import ServiceContainer
from app.utils.yaml_loader import YamlLoaderMixin

class TTSService(YamlLoaderMixin):
    """
    Clase para gestionar la conversión de texto a audio usando la API Play.ht.

    Args:
        YamlLoaderMixin: Clase base para cargar configuraciones desde archivos YAML.
    """

    def __init__(self, services: ServiceContainer, voices: dict):
        """
        Inicializa la instancia de TTSService.
        Args:
            services (ServiceContainer): Contenedor de servicios que incluye la base de datos y el servicio de archivos.
        """
        self.voices = voices
        self.services = services

        # Inicializar proveedores
        config = self.load_yaml('config.yaml')

        self.providers = {
            'playht': PlayHTProvider(config['api']['tts_providers']['playht']),
            'polly': PollyProvider(config['api']['tts_providers']['polly']),
            'voicemaker': VoicemakerProvider(config['api']['tts_providers']['voicemaker'])
        }

    def generate_audio_from_text(self, request:TextToSpeechRequestById , model:InformationModel) -> str:
        """
        Genera un archivo de audio a partir de un texto utilizando un modelo de texto a voz.
        Este método verifica si el audio ya existe en la base de datos y, si no, lo genera
        utilizando el modelo de voz especificado.
        Args:
            request (TextToSpeechRequestById): Objeto de solicitud que contiene el texto a procesar.
            model (InformationModel): Modelo de información con los detalles de la voz a utilizar.
        Returns:
            str: La URL del archivo de audio generado.
        Raises:
            ValueError: Si ocurre un error durante la generación del audio.
        """
        read_text = request.read
        audio_name = read_text + model.language[:2] + str(model.id) + model.voice_name + model.gender
        audio_hash = self.services.file_service.generate_hash(audio_name)

        # Verificar si el audio ya existe en la base de datos
        existing_audio = self.services.db_service.get_audio_by_hash(audio_hash)
        if existing_audio and 'file_url' in existing_audio:
            return existing_audio['file_url']
        
        # Generar el audio con la voz seleccionada
        audio_file_url = self.synthesize_audio(request, model, read_text, audio_hash)
        return audio_file_url
                
    def synthesize_audio(self, request: TextToSpeechRequestById, model: InformationModel, read_text: str, audio_hash: str) -> str:
        """
        Genera el audio a partir del texto utilizando el proveedor correspondiente.
        Args:
            request (TextToSpeechRequestById): Objeto de solicitud que contiene el texto a procesar.
            model (InformationModel): Modelo de información con los detalles de la voz a utilizar.
            read_text (str): Texto a convertir en audio.
            audio_hash (str): Hash único del audio.
        Returns:
            str: La URL del archivo de audio generado.
        """
        # Limpiar espacios al inicio y al final
        read_text = read_text.strip()
        if not read_text.endswith('.'):
            read_text += '.'

        # Generar el nombre del archivo de audio, 
        audio_name = read_text + model.model
        audio_path = self.services.file_service.get_audio_path(audio_name)

        # Obtener el proveedor correspondiente
        provider = self.providers.get(model.platform)
        if not provider:
            raise ValueError(f"Plataforma no soportada: {model.platform}")

        try:
            api_request = provider.build_request(read_text, model)
            response = provider.execute_request(api_request)

            self.save_audio_from_response(response, audio_path)

            return self._upload_and_save(
                request=request,
                model=model,
                file_path=audio_path,
                audio_hash=audio_hash
            )
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error al llamar a la API: {e}")
        except Exception as e:
            raise ValueError(f"Error al procesar el texto a audio: Tokens agotados, suscripción o parametros no validos. Detalles:{e}")
        
    @staticmethod
    def save_audio_from_response(response, audio_path: str):
        """
        Guarda el audio recibido de la respuesta de la API en un archivo local.
        Este método procesa el contenido de la respuesta en chunks y los escribe en el archivo especificado.
        Args:
            response (requests.Response): Objeto de respuesta de la API que contiene el audio.
            audio_path (str): Ruta completa donde se guardará el archivo de audio.
        Raises:
            ValueError: Si ocurre un error al escribir el archivo en el disco.
        """
        try:
            with open(audio_path, "wb") as audio_file:
                for chunk in response.iter_content(chunk_size=8192):
                    audio_file.write(chunk)
        except Exception as e:
            raise ValueError(f"Error al guardar el archivo de audio: {e}")
        
    def save_files(self, files: Dict[str, str], model:InformationModel, path: str) -> bool:
        """
        Guarda una lista de archivos en el sistema de archivos y los registra en la base de datos.

        Args:
            files (Dict[str, str]): Diccionario con clave como texto y valor como ruta del archivo generado.
            model (InformationModel): Modelo con los detalles de la voz a utilizar.
            path (str): Ruta del directorio donde se guardarán los archivos temporales.
        Returns:
            bool: True si se guardaron todos correctamente.
        """
        for key, name in files.items():
            filename, ext = os.path.splitext(name)
            text, _ = os.path.splitext(key)

            audio_path = os.path.join(path, f"{filename}{ext}")
            if self._audio_exists(filename):
                self._delete_temp_file(audio_path)
                continue

            request = TextToSpeechRequestById(read=text, text=text)
            self._upload_and_save(request, model, audio_path, filename)

        return True

    def _delete_temp_file(self, file_path: str) -> None:
        """
        Elimina un archivo temporal del sistema de archivos.

        Args:
            file_path (str): Ruta del archivo a eliminar.
        Raises:
            OSError: Si ocurre un error al eliminar el archivo.
        """
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Advertencia: No se pudo eliminar el archivo temporal {file_path}: {e}")

    def _audio_exists(self, audio_hash: str) -> bool:
        """
        Verifica si un archivo de audio ya existe en la base de datos.

        Args:
            audio_hash (str): Hash único del audio a verificar.
        Returns:
            bool: True si el audio existe, False en caso contrario.
        """
        return self.services.db_service.get_audio_by_hash(audio_hash) is not None
    
    # Guarda un archivo de audio y lo registra en la base de datos.
    def _upload_and_save(self, request: TextToSpeechRequestById, model: InformationModel, file_path: str, audio_hash: str) -> str:
        """
        Guarda un archivo de audio y lo registra en la base de datos.
        
        Args:
            request (TextToSpeechRequestById): Objeto de solicitud que contiene el texto a procesar.
            model (InformationModel): Modelo de información con los detalles de la voz a utilizar.
            file_path (str): Ruta del archivo de audio a guardar.
            audio_hash (str): Hash único del audio.
        Returns:
            str: La URL del archivo de audio generado.
        Raises:
            ValueError: Si ocurre un error al guardar el registro en la base de datos.
        """
        audio_file_url = self.services.s3_service.upload_audio(str(file_path), audio_hash)
        self._delete_temp_file(file_path)

        if not self.services.db_service.save_generated_audio(
            request, model, file_url=audio_file_url, audio_hash=audio_hash
        ):
            raise ValueError("Error: No se pudo guardar el registro de audio en la base de datos")

        return audio_file_url