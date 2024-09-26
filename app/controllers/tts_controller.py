from fastapi import APIRouter, HTTPException
from app.models.tts_model import TextToSpeechRequest
from app.services.tts_service import TTSService

router = APIRouter()
tts_service = TTSService()

@router.post("/tts/")
async def create_tts(request: TextToSpeechRequest):
    output_path = "app/resources/audio.wav"
    model = request.model if request.model is not None else 2
    try:
        tts_service.synthesize(request.text, model, output_path)
        return {"message": "Audio synthesized successfully", "audio_path": output_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
