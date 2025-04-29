import json
import mysql.connector
from app.models.information_model import CreateVoiceModel, InformationModel
from app.models.tts_model import TextToSpeechRequestById
from app.utils.yaml_loader import YamlLoaderMixin
from datetime import datetime
from typing import Dict, List, Optional, Set

class DBService(YamlLoaderMixin):
    """
    Servicio para manejar las conexiones y operaciones con la base de datos MySQL.
    """
    
    def __init__(self, db_config: dict):
        """
        Inicializa la conexión a la base de datos usando la configuración del archivo YAML.
        Args:
            db_config (dict): Configuración de la base de datos.
        """
        self.connection = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
        )
        # Caché ligero solo para verificación de existencia
        self._hash_set: Set[str] = set()
        # Caché de URLs para acceso rápido
        self._url_cache: Dict[str, str] = {}  # {hash: file_url}
        self._initialize_cache()

    def _initialize_cache(self) -> None:
        """Carga solo los hashes y URLs en memoria"""
        cursor = self.connection.cursor(dictionary=True)
        sql = "SELECT audio_hash, file_url FROM generated_audios"
        
        try:
            cursor.execute(sql)
            results = cursor.fetchall()

            # Poblar ambos cachés
            self._hash_set = {row['audio_hash'] for row in results}
            self._url_cache = {row['audio_hash']: row['file_url'] for row in results}

            print(f"Cache inicializado con {len(self._hash_set)} registros")
        except mysql.connector.Error as err:
            print(f"Error inicializando cache: {err}")
            self._hash_set = set()
            self._url_cache = {}
        finally:
            cursor.close()

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
    
    def save_generated_audio(self, request:TextToSpeechRequestById, 
                             model:InformationModel, 
                             file_url:str, 
                             audio_hash:str) -> bool:
        """
        Guarda un registro de audio generado en la base de datos.
        Args:
            request (TextToSpeechRequestById): Objeto de solicitud que contiene el texto a procesar.
            model (InformationModel): Modelo de información con los detalles de la voz a utilizar.
            file_url (str): URL del archivo de audio generado.
            audio_hash (str): Hash único del audio.
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        cursor = self.connection.cursor()
        sql = """INSERT INTO generated_audios 
                 (original_text, input_text, information_id, file_url, audio_hash) 
                 VALUES (%s, %s, %s, %s, %s)"""
        values = (request.text, request.read, model.id, file_url, audio_hash)
        
        try:
            cursor.execute(sql, values)
            self.connection.commit()

            # Actualizar ambos cachés
            self._hash_set.add(audio_hash)
            self._url_cache[audio_hash] = file_url
            
            return True
        except mysql.connector.Error as err:
            print(f"Error al guardar en la base de datos: {err}")
            return False
        finally:
            cursor.close()

    def get_audio_by_hash(self, audio_hash: str) -> Optional[dict]:
        """
        Busca un registro de audio por su hash, primero en caché y luego en BD si no existe.
        Args:
            audio_hash (str): Hash único del audio a buscar
        Returns:
            Optional[dict]: Diccionario con los datos del audio si existe, None si no se encuentra
        """
        # Verificar si existe el hash
        if audio_hash not in self._hash_set:
            return None

        # Si solo necesitamos la URL, la retornamos del caché
        cached_url = self._url_cache.get(audio_hash)
        if cached_url:
            return {'file_url': cached_url, 'audio_hash': audio_hash}

        # Solo si se necesitan más detalles, consultamos la BD
        return self._fetch_full_details(audio_hash)
    
    def _fetch_full_details(self, audio_hash: str) -> Optional[dict]:
        """Obtiene todos los detalles de un audio de la BD"""
        cursor = self.connection.cursor(dictionary=True)
        sql = "SELECT * FROM generated_audios WHERE audio_hash = %s LIMIT 1"
        
        try:
            cursor.execute(sql, (audio_hash,))
            result = cursor.fetchone()
            if result:
                # Actualizar caché de URL si no existe
                self._url_cache[audio_hash] = result['file_url']
            return result
        except mysql.connector.Error as err:
            print(f"Error en BD: {err}")
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

            # Process metadata field for each row
            processed_rows = []
            for row in result:
                if row.get('metadata') and isinstance(row['metadata'], str):
                    try:
                        row['metadata'] = json.loads(row['metadata'])
                    except json.JSONDecodeError:
                        pass
                processed_rows.append(row)
                
            return [InformationModel(**row) for row in processed_rows]
    
        except mysql.connector.Error as err:
            print(f"Error al buscar en la base de datos: {err}")
            return None
        finally:
            cursor.close()
    
    def refresh_cache(self) -> None:
        """
        Actualiza completamente el caché desde la base de datos.
        Útil cuando se sospecha que el caché puede estar desactualizado.
        """
        self._initialize_cache()

    def __del__(self):
        """
        Cierra la conexión a la base de datos cuando se destruye la instancia.
        """
        if hasattr(self, 'connection') and self.connection.is_connected():
            self.connection.close() 