import json
from fastapi import APIRouter, HTTPException
from app.models.tts_model import TextToSpeechRequest
from app.services.tts_service import TTSService
from app.services.file_service import FileService
from pathlib import Path

output_dir = "app/resources/audios"
router = APIRouter()
file_service = FileService(output_dir)
tts_service = TTSService(file_service)

@router.post("/tts/")
async def create_tts(request: TextToSpeechRequest):
    output_path = "app/resources/audio.wav"
    model = request.model if request.model is not None else 21
    try:
        # Verifica si ya existe un audio para el texto
        audio_path = tts_service.synthesize(request.text, model)
        return {"message": "Audio synthesized successfully", "audio_path": audio_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/models/")
async def get_all_models():
    try:
        models_path = Path("app/data/model.json")
        with models_path.open(encoding="utf-8") as json_file:
            data = json.load(json_file)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al cargar los modelos")
