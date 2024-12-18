from fastapi import APIRouter, HTTPException
from app.models.tts_model import TextToSpeechRequest
from app.services.tts_service import TTSService
from app.services.file_service import FileService
from app.services.s3_service import S3Service
from app.services.db_service import DBService
from ..utils.yaml_loader import YamlLoaderMixin

class AppConfig(YamlLoaderMixin):
    """Clase para cargar la configuración de voces desde un archivo YAML.
    Hereda de YamlLoaderMixin para reutilizar la carga de archivos YAML.
    """
    pass

app_config = AppConfig()
voices = app_config.load_yaml('app/data/voices_config.yaml')['voices']
aws_config = app_config.load_yaml('config.yaml')['aws']
db_config = app_config.load_yaml('config.yaml')['db']['mysql']

output_dir = "app/resources/audios"
router = APIRouter()

file_service = FileService(output_dir)
s3_service = S3Service(aws_config)
db_service = DBService(db_config)
tts_service = TTSService(file_service, s3_service, db_service)

@router.post("/tts/")
async def create_tts(request: TextToSpeechRequest):
    """Genera el archivo de audio a partir de un texto.
    Recibe una solicitud POST con los parámetros de texto, idioma, género y modelo para generar
    el audio sintetizado. Si el archivo de audio ya existe, se retorna la ruta del archivo.
    Args:
        request (TextToSpeechRequest): Objeto que contiene el texto, idioma, género y modelo.
    Returns:
        dict: Un mensaje con la ruta del archivo de audio generado.
    Raises:
        HTTPException: Si ocurre un error durante la generación del audio, se lanza una excepción.
    """
    (text, language, gender, model) = (request.text, request.language, request.gender, request.model)
    try:
        # Verifica si ya existe un audio para el texto
        audio_path = tts_service.generate_audio_from_text(text, language, gender, model)
        return {"message": "Audio synthesized successfully", "audio_path": audio_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/")
async def get_all_models():
    """Devuelve una lista de los modelos de voces disponibles.
    Retorna todos los modelos de voz disponibles que están cargados desde el archivo de configuración YAML.
    Returns:
        list: Lista de modelos de voz disponibles.
    Raises:
        HTTPException: Si ocurre un error al cargar los modelos, se lanza una excepción.
    """
    try:
        return voices
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al cargar los modelos")
