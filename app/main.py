from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.controllers.tts_controller import router as tts_router

app = FastAPI()

# Configuración de CORS
origins = [
    "http://181.143.15.106",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/app/resources", StaticFiles(directory="app/resources"), name="resources")

app.include_router(tts_router)