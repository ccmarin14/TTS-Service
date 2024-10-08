# app/static_files.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

static_app = FastAPI()

# Montar la ruta de recursos estáticos
static_app.mount("/app/resources", StaticFiles(directory="app/resources"), name="resources")