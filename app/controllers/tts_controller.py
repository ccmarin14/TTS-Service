from typing import Dict, List
from fastapi import APIRouter, HTTPException
from app.models.information_model import information_model
from app.models.tts_model import TextToSpeechRequestById, TextToSpeechRequestByName, TextToSpeechRequestOptional
from app.services.container_service import ServiceContainer
from app.services.database.query_service import QueryService
from app.services.tts.tts_service import TTSService
from app.validators.tts_validator import TTSValidator
from ..utils.yaml_loader import YamlLoaderMixin

class AppConfig(YamlLoaderMixin):
    """Clase para cargar la configuración de voces desde un archivo YAML.
    Hereda de YamlLoaderMixin para reutilizar la carga de archivos YAML.
    """
    pass

app_config = AppConfig()
aws_config = app_config.load_yaml('config.yaml')['aws']
db_config = app_config.load_yaml('config.yaml')['db']['mysql']

output_dir = "app/resources/audios"
router = APIRouter()

# Crear el contenedor de servicios
service_container = ServiceContainer(
    output_dir=output_dir,
    aws_config=aws_config,
    db_config=db_config
)

# Obtener el listado de los modelos
voices = service_container.db_service.get_models()

# Crear el servicio TTS usando el contenedor
tts_service = TTSService(service_container, voices)
tts_validator = TTSValidator()

@router.post("/tts/by-name/")
async def create_tts_by_name(request: TextToSpeechRequestByName) -> dict:
    """Genera un archivo de audio usando el nombre del modelo.
    Args:
        request (TextToSpeechRequestByName): Objeto con el texto, lenguaje y nombre del modelo.
    Returns:
        dict: Mensaje con la ruta del archivo de audio generado.
    """
    try:
        tts_validator.validate_request_by_name(request)
        
        model = next((m for m in voices if (m.language == request.language and m.voice_name == request.model)), None)
        if not model:
            raise HTTPException(
                status_code=404, 
                detail=f"Información no encontrada para el lenguage:'{request.language}' y para el nombre del modelo:'{request.model}'"
            )
        
        audio_path = tts_service.generate_audio_from_text(request, model)
        return {"message": "Audio sintentizado correctamente", "audio_path": audio_path}
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tts/optional/")
async def create_tts_optional(request: TextToSpeechRequestOptional) -> dict: 
    """Genera un archivo de audio con parámetros opcionales.
    Args:
        request_option (dict): Objeto con texto y parámetros opcionales(lenguaje, genero y tipo).
    Returns:
        dict: Mensaje con la ruta del archivo de audio generado.
    """
    try:
        tts_validator.validate_request_optional(request)

        model = next((m for m in voices if (m.language == request.language and m.gender == request.gender and m.type == request.type)), None)
        if not model:
            raise HTTPException(
                status_code=404, 
                detail=f"Información no encontrada para el lenguage:'{request.language}' para el genero :'{request.gender}' y del tipo:'{request.type}'"
            )

        audio_path = tts_service.generate_audio_from_text(request, model)
        return {"message": "Audio sintentizado correctamente", "audio_path": audio_path}
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tts/{model_id}")
async def create_tts_by_id(model_id: int, request: TextToSpeechRequestById) -> dict:
    """Genera un archivo de audio usando el ID del modelo.
    Args:
        model_id (int): ID del modelo de voz a utilizar
        request (TextToSpeechRequestById): Objeto con el texto a sintetizar
    Returns:
        dict: Mensaje con la ruta del archivo de audio generado.
    Raises:
    HTTPException: 
        - 404 Si el modelo especificado no exites
        - 500 Si hubo al momento de sintetizar el audio
    """
    try:
        tts_validator.validate_request_by_id(request)

        model = next((m for m in voices if m.id == model_id), None)
        if not model:
            raise HTTPException(status_code=404, detail=f"Modelo con el id:{model_id} no encontrado")
            
        audio_path = tts_service.generate_audio_from_text(request, model)
        
        return {"message": "Audio sintentizado correctamente", "audio_path": audio_path}
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/")
async def get_all_models() -> Dict:
    """Obtiene todos los modelos de voz disponibles.
    Returns:
        List[information_model]: Lista de modelos de voz disponibles.
    Raises:
        HTTPException: Si ocurre un error al recuperar los modelos.
    """
    try:
        return QueryService.organize_voice_models(voices)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al cargar los modelos")
