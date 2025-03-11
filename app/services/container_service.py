from app.services.storage.file_service import FileService
from app.services.tts.s3_service import S3Service
from app.services.database.db_service import DBService

class ServiceContainer:
    """
    Contenedor que encapsula y gestiona todos los servicios de la aplicación.
    
    Este contenedor implementa el patrón Registry para centralizar el acceso
    a los servicios y facilitar la inyección de dependencias.
    """
    
    def __init__(self, output_dir: str, aws_config: dict, db_config: dict):
        """
        Inicializa el contenedor y crea todas las instancias de los servicios.
        
        Args:
            output_dir (str): Directorio para archivos de audio
            aws_config (dict): Configuración de AWS
            db_config (dict): Configuración de la base de datos
        """
        self._file_service = FileService(output_dir)
        self._s3_service = S3Service(aws_config)
        self._db_service = DBService(db_config)

    @property
    def file_service(self) -> FileService:
        """Acceso al servicio de archivos"""
        return self._file_service

    @property
    def s3_service(self) -> S3Service:
        """Acceso al servicio de S3"""
        return self._s3_service

    @property
    def db_service(self) -> DBService:
        """Acceso al servicio de base de datos"""
        return self._db_service