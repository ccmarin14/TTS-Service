import mysql.connector
from typing import List
from app.models.information_model import information_model
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
            database=db_config['database']
        )
    
    def save_generated_audio(self, request:TextToSpeechRequestById, model:information_model, file_url:str, audio_hash:str) -> bool:
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

    def get_models(self) -> List[information_model]:
        """
        Obtiene todos los modelos de información de audio disponibles.
        Returns:
            List[information_model]: Lista de modelos de información, None si hay error
        """
        cursor = self.connection.cursor(dictionary=True)
        sql = """
                SELECT * FROM information_audios 
            """
    
        try:
            cursor.execute(sql)
            result = cursor.fetchall()
            return [information_model(**row) for row in result]
    
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