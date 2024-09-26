from fastapi import FastAPI
from app.controllers.tts_controller import router as tts_router

app = FastAPI()

app.include_router(tts_router)