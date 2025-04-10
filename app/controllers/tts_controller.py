from typing import Dict, List
from fastapi import APIRouter, HTTPException, UploadFile
from app.models.information_model import CreateVoiceModel, InformationModel
from app.models.tts_model import TextToSpeechRequestById, TextToSpeechRequestByName, TextToSpeechRequestOptional
from app.services.container_service import ServiceContainer
from app.services.tts.tts_service import TTSService
from app.services.zip_service import ZipService
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

@router.post("/tts/upload-zip/{model_id}")
async def upload_zip_model(model_id: int, file: UploadFile) -> Dict:
    """Carga un archivo ZIP y lo procesa para el modelo de voz especificado.
    Args:
        model_id (int): ID del modelo de voz a utilizar
        file (UploadFile): Archivo ZIP a cargar
    Returns:
        Dict: Mensaje de éxito y lista de archivos extraídos
    Raises:
        HTTPException: 
            - 422 Si el archivo ZIP no es válido
            - 404 Si el modelo especificado no existe
            - 500 Si hubo un error al procesar el archivo ZIP
    """
    try:
        # Validar que el modelo exista
        model = next((m for m in voices if m.id == model_id), None)
        if not model:
            raise HTTPException(status_code=404, detail=f"Modelo con el id:{model_id} no encontrado")

        zip_service = ZipService()
        
        # Validar el archivo zip
        await zip_service.validate_zip_file(file)

        # Extraer archivos
        files = await zip_service.extract_zip(file, model)

        tts_service.save_files(files, model, zip_service.UPLOAD_DIR)

        return {
            "message": "Archivo zip cargado correctamente",
            "extracted_files": files,
        }
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/models/")
async def create_voice_model(voice_model: CreateVoiceModel) -> Dict:
    """
    Crea un nuevo modelo de voz.
    Args:
        voice_model (CreateVoiceModel): Datos del nuevo modelo de voz
    Returns:
        Dict: Datos del modelo creado
    Raises:
        HTTPException: 
            - 422 Si los datos son inválidos
            - 500 Si hay un error al crear el modelo
    """
    try:
        # Validar que no exista un modelo con el mismo nombre
        existing_model = next(
            (m for m in voices if m.voice_name == voice_model.voice_name), 
            None
        )
        
        if existing_model:
            raise ValueError(f"Ya existe un modelo con el nombre: {voice_model.voice_name}")

        # Crear el nuevo modelo
        new_model = service_container.db_service.save_voice_model(voice_model)
        if not new_model:
            raise ValueError("No se pudo crear el modelo")

        # Actualizar la lista de voces en memoria
        voices.append(new_model)

        return {
            "message": "Modelo creado correctamente",
            "model": new_model
        }

    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al crear el modelo: {str(e)}"
        )

@router.get("/models/")
async def get_all_models() -> List[InformationModel]:
    """Obtiene todos los modelos de voz disponibles.
    Returns:
        List[InformationModel]: Lista de modelos de voz disponibles.
    Raises:
        HTTPException: Si ocurre un error al recuperar los modelos.
    """
    try:
        return voices
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al cargar los modelos")

