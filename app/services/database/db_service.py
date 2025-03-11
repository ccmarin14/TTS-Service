import mysql.connector
from typing import List
from app.models.information_model import CreateVoiceModel, InformationModel
from app.models.tts_model import TextToSpeechRequestById
from app.utils.yaml_loader import YamlLoaderMixin

class DBService(YamlLoaderMixin):
    """
    Servicio para manejar las conexiones y operaciones con la base de datos MySQL.
    """
    
    def __init__(self, db_config: dict):
        """
        Inicializa la conexión a la base de datos usando la configuración del archivo YAML.
        """
        self.connection = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
        )

    def save_voice_model(self, voice_model:CreateVoiceModel) -> CreateVoiceModel:
        """
        Guarda un nuevo modelo de voz en la base de datos.
        Args:
            voice_model (InformationModel): Datos del nuevo modelo de voz
        Returns:
            InformationModel: Modelo creado con su ID si fue exitoso, None si hubo error
        """
        cursor = self.connection.cursor(dictionary=True)
        sql = """INSERT INTO information_audios 
                 (voice_name, language, gender, type, platform, model) 
                 VALUES (%s, %s, %s, %s, %s, %s)"""
        values = (
            voice_model.voice_name,
            voice_model.language,
            voice_model.gender,
            voice_model.type,
            voice_model.platform,
            voice_model.model
        )
        
        try:
            cursor.execute(sql, values)
            self.connection.commit()
            
            # Obtener el modelo recién creado
            new_id = cursor.lastrowid
            cursor.execute("SELECT * FROM information_audios WHERE id = %s", (new_id,))
            result = cursor.fetchone()
            
            return CreateVoiceModel(**result) if result else None
            
        except mysql.connector.Error as err:
            print(f"Error al guardar el modelo en la base de datos: {err}")
            return None
        finally:
            cursor.close()
    
    def save_generated_audio(self, request:TextToSpeechRequestById, model:InformationModel, file_url:str, audio_hash:str) -> bool:
        """
        Guarda un registro de audio generado en la base de datos.
        Args:
            text (str): Texto utilizado para generar el audio
            language (str): Idioma del audio
            gender (str): Género de la voz
            model (str): Modelo de voz utilizado
            file_url (str): URL del archivo de audio
            audio_hash (str): Hash único del audio
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        text = request.text
        read_text = request.read
        cursor = self.connection.cursor()
        sql = """INSERT INTO generated_audios 
                 (original_text, input_text, information_id, file_url, audio_hash) 
                 VALUES (%s, %s, %s, %s, %s)"""
        values = (text, read_text, model.id, file_url, audio_hash)
        
        try:
            cursor.execute(sql, values)
            self.connection.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error al guardar en la base de datos: {err}")
            return False
        finally:
            cursor.close()

    def get_audio_by_hash(self, audio_hash: str) -> dict:
        """
        Busca un registro de audio por su hash en la base de datos.
        Args:
            audio_hash (str): Hash único del audio a buscar
        Returns:
            dict: Diccionario con los datos del audio si existe, None si no se encuentra
        """
        cursor = self.connection.cursor(dictionary=True)
        sql = """SELECT * FROM generated_audios 
                WHERE audio_hash = %s 
                LIMIT 1"""
        
        try:
            cursor.execute(sql, (audio_hash,))
            result = cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            print(f"Error al buscar en la base de datos: {err}")
            return None
        finally:
            cursor.close()

    def get_models(self) -> List[InformationModel]:
        """
        Obtiene todos los modelos de información de audio disponibles.
        Returns:
            List[InformationModel]: Lista de modelos de información, None si hay error
        """
        cursor = self.connection.cursor(dictionary=True)
        sql = """
                SELECT * FROM information_audios 
            """
    
        try:
            cursor.execute(sql)
            result = cursor.fetchall()
            return [InformationModel(**row) for row in result]
    
        except mysql.connector.Error as err:
            print(f"Error al buscar en la base de datos: {err}")
            return None
        finally:
            cursor.close()

    def __del__(self):
        """
        Cierra la conexión a la base de datos cuando se destruye la instancia.
        """
        if hasattr(self, 'connection') and self.connection.is_connected():
            self.connection.close() 