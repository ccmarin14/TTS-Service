from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.controllers.tts_controller import router as tts_router

app = FastAPI()

@app.middleware("http")
async def prioritize_get_requests(request: Request, call_next):
    if request.method == "GET" and request.url.path.startswith("/app/resources/audios"):
        response = await call_next(request)
        return response
    else:
        return await call_next(request)

# Configuración de CORS
origins = [
    "http://181.143.15.106",
    "http://181.143.15.106:5500",
    "http://127.0.0.1:5500",
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