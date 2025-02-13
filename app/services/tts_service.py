import requests
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

    def __init__(self, file_service: 'FileService', s3_service: 'S3Service', db_service: 'DBService'):
        """
        Inicializa la instancia de TTSService.
        Args:
            file_service (FileService): Una instancia para gestionar los archivos generados.
        """
        self.voices = self.load_yaml('app/data/voices_config.yaml')['voices']
        self.api = self.load_yaml('config.yaml')['api']
        self.file_service = file_service
        self.s3_service = s3_service
        self.db_service = db_service

    def generate_audio_from_text(self, text, language, gender, model):
        """
        Genera un archivo de audio a partir de un texto utilizando un modelo de texto a voz.
        Este método selecciona una voz adecuada basada en el idioma, género y modelo especificados, 
        y luego genera un archivo de audio con el texto proporcionado.
        Args:
            text (str): El texto que se convertirá en audio.
            language (str): El idioma del texto (por ejemplo, 'en-US', 'es-ES').
            gender (str): El género de la voz (por ejemplo, 'M' para masculino, 'F' para femenino).
            model (str): El identificador del modelo de voz. Si se proporciona, se utiliza este modelo directamente.
        Returns:
            str: La URL o la ruta del archivo de audio generado.
        Raises:
            ValueError: Si no se encuentra una voz adecuada o ocurre un error durante la generación del audio.
        """
        # Selección de la voz usando la configuración del archivo YAML
        selected_voice = self.select_voice(language, gender, model)

        # Generar el hash del audio
        audio_hash = self.file_service.generate_hash(text + selected_voice)

        # Verificar si el audio ya existe en la base de datos
        existing_audio = self.db_service.get_audio_by_hash(audio_hash)
        if existing_audio:
            return existing_audio['file_url']
        
        # Generar el audio con la voz seleccionada
        audio_file_url = self.synthesize_audio(text, selected_voice)

        # Guardar el registro en la base de datos usando el servicio
        self.db_service.save_generated_audio(
            text=text,
            language=language,
            gender=gender,
            model=model or selected_voice,
            file_url=audio_file_url,
            audio_hash=audio_hash
        )
        
        return audio_file_url
        
    def select_voice(self, language, gender, model):
        """
        Selecciona una voz para el texto a sintetizar.
        Si se pasa un modelo específico, se utiliza este. De lo contrario,
        selecciona una voz basada en el idioma y género desde la configuración.
        Args:
            language (str): Idioma de la voz (e.g., 'en-US', 'es-ES').
            gender (str): Género de la voz (e.g., "M", "F").
            model (str, optional): ID de un modelo específico. Por defecto, None.
        Returns:
            str: ID de la voz seleccionada.
        Raises:
            KeyError: Si no se encuentra una voz que coincida con los criterios.
        """
        # Si se pasa un modelo específico, lo seleccionamos
        if model:
            return model
        
        # Si no se pasa un modelo, seleccionamos uno del archivo de configuración
        try:
            # Obtener la lista de voces según el idioma y género
            available_voices = self.voices[language][gender]
            return available_voices[0]['id']
        except KeyError:
            # Si no se encuentra la configuración, devolvemos una voz por defecto
            return "DefaultVoice"
                
    def synthesize_audio(self, text: str, selected_voice:str):
        """
        Genera un archivo de audio a partir de un texto dado.
        Args:
            text (str): Texto a convertir en audio.
            selected_voice (str): ID de la voz seleccionada.
        Returns:
            str: Ruta del archivo de audio generado.
        Raises:
            ValueError: Si la API devuelve un error o falla el proceso de síntesis.
        """
        # Limpiar espacios al inicio y al final
        text = text.strip()
        
        if not text.endswith('.'):
            text += '.'

        audio_name = text + selected_voice

        # Generar el hash del texto
        audio_path = self.file_service.get_audio_path(audio_name)
        audio_name = self.file_service.generate_hash(audio_name)

        # Construir la solicitud a la API
        request = self.build_request(text, selected_voice)

        try:
            # Llamada a la API de Play.ht
            response = requests.post(request['url'], headers=request['headers'], json=request['payload'], stream=True)
            if response.status_code != 200:
                raise ValueError(f"Error al llamar a la API: {response.text}")
            
            # Guardar el audio retornado por la API
            self.save_audio_from_response(response, audio_path)
            s3_url = self.s3_service.upload_audio(str(audio_path), audio_name)
            
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
            raise ValueError(f"Error al procesar el texto a audio: {e}")
        
    def build_request(self, text, selected_voice):
        """
        Construye los datos necesarios para realizar una solicitud a la API.
        Este método organiza la URL, los encabezados y el cuerpo de la solicitud
        para interactuar con la API Play.ht.
        Args:
            text (str): Texto a convertir en audio.
            selected_voice (str): ID de la voz seleccionada.
        Returns:
            dict: Diccionario con la URL, encabezados y el cuerpo de la solicitud.
        """
        request = {}
        request['url'] = self.api['url']
        request['headers'] = {
            "Content-Type": self.api['headers']['Content-Type'],
            "X-USER-ID": self.api['credentials']['X-USER-ID'],
            "AUTHORIZATION": self.api['credentials']['AUTHORIZATION'],
            "accept": self.api['headers']['accept'],
        }
        request['payload'] = {
            "voice_engine": self.api['defaults']['voice_engine'],
            "output_format": self.api['defaults']['output_format'],
            "speed": self.api['defaults']['speed'],
            "text": text,
            "voice": selected_voice
        }
        return request
    
    def save_audio_from_response(self, response, audio_path: str):
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
