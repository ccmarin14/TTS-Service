from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.controllers.tts_controller import router as tts_router
from app.utils.yaml_loader import YamlLoaderMixin
from dotenv import load_dotenv

# Cargar variables de entorno al inicio
load_dotenv()

class AppConfig(YamlLoaderMixin):
    """Configuración de la aplicación.
    Hereda de `YamlLoaderMixin` para cargar la configuración desde un archivo YAML.
    """
    pass

# Inicialización de la aplicación FastAPI
app = FastAPI()

# Cargar la configuración de la API desde el archivo YAML
app_config = AppConfig()
api = app_config.load_yaml('config.yaml')['api']

# Configuración de CORS
origins = api['cors']['origins']

# Agregar middleware CORS para permitir solicitudes de múltiples orígenes
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Orígenes permitidos desde el archivo de configuración
    allow_credentials=True,  # Permitir el uso de credenciales en las solicitudes
    allow_methods=["*"],     # Permitir todos los métodos HTTP
    allow_headers=["*"],     # Permitir todos los encabezados HTTP
)

# Montar el directorio estático para servir archivos como audios o recursos
app.mount("/app/resources", StaticFiles(directory="app/resources"), name="resources")

# Incluir las rutas definidas en el controlador de TTS (Text to Speech)
app.include_router(tts_router)