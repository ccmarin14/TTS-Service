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

    Atributos:
        voices (dict): Configuración de voces cargada desde un archivo YAML.
        api (dict): Configuración de la API cargada desde un archivo YAML.
        file_service (FileService): Servicio para gestionar los archivos de audio.
        db_service (DBService): Una instancia para gestionar la base de datos.
    """

    def __init__(self, services: ServiceContainer, voices: dict):
        """
        Inicializa la instancia de TTSService.
        Args:
            file_service (FileService): Una instancia para gestionar los archivos generados.
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

        # Generar el hash del audio
        audio_hash = self.services.file_service.generate_hash(read_text + model.model)

        # Verificar si el audio ya existe en la base de datos
        existing_audio = self.services.db_service.get_audio_by_hash(audio_hash)
        if existing_audio:
            return existing_audio['file_url']
        
        # Generar el audio con la voz seleccionada
        audio_file_url = self.synthesize_audio(read_text, model)

        # Guardar el registro en la base de datos usando el servicio
        if not self.services.db_service.save_generated_audio(
            request,
            model,
            file_url=audio_file_url,
            audio_hash=audio_hash
        ):
            raise ValueError("Error: No se pudo guardar el registro de audio en la base de datos")
        
        return audio_file_url
                
    def synthesize_audio(self, read_text: str, model:InformationModel) -> str:
        """
        Genera un archivo de audio a partir de un texto dado.
        Args:
            read_text (str): Texto a convertir en audio.
            selected_voice (str): ID de la voz seleccionada.
        Returns:
            str: Ruta del archivo de audio generado.
        Raises:
            ValueError: Si la API devuelve un error o falla el proceso de síntesis.
        """
        # Limpiar espacios al inicio y al final
        read_text = read_text.strip()
        
        if not read_text.endswith('.'):
            read_text += '.'

        audio_name = read_text + model.model

        # Generar el hash del texto
        audio_path = self.services.file_service.get_audio_path(audio_name)
        audio_name = self.services.file_service.generate_hash(audio_name)

        # Obtener el proveedor correspondiente
        provider = self.providers.get(model.platform)
        if not provider:
            raise ValueError(f"Plataforma no soportada: {model.platform}")

        try:
            # Construir la solicitud a la API
            request = provider.build_request(read_text, model)

            # Llamada a la API de la plataforma seleccionada
            response = provider.execute_request(request)
            
            # Guardar el audio retornado por la API
            self.save_audio_from_response(response, audio_path)
            s3_url = self.services.s3_service.upload_audio(str(audio_path), audio_name)
            
            # Eliminar el archivo temporal
            try:
                import os
                os.remove(audio_path)
            except Exception as e:
                print(f"Advertencia: No se pudo eliminar el archivo temporal {audio_path}: {e}")

            return str(s3_url)
        
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
