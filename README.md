# Servicio de TTS

## Descripción
Este proyecto es un backend desarrollado con FastAPI, siguiendo el patrón de diseño Modelo-Vista-Controlador (MVC). Su principal objetivo es proporcionar un servicio de Text-to-Speech (TTS) que permite convertir texto en audio.

## Estructura del Proyecto
`/TTS-Service`

-   **app/**
    -   `__init__.py`
    -   `main.py`: Archivo principal donde se inicializa FastAPI.
    -   **models/**: Carpeta para modelos de datos.
        -   `__init__.py`
        -   `tts_model.py`: Definición de modelos usando Pydantic.
    -   **services/**: Carpeta para la lógica del negocio.
        -   `__init__.py`
        -   `tts_service.py`: Lógica para manejar TTS, incluyendo la configuración de modelos y la síntesis de audio.
    -   **controllers/**: Carpeta para controladores (rutas).
        -   `__init__.py`
        -   `tts_controller.py`: Rutas relacionadas con TTS, donde se gestionan las solicitudes de síntesis de audio.
    -   **resources/**: Carpeta para almacenar archivos de audio generados.
        -   `audio.wav`: Archivo de audio sintetizado.
    -   **utils/**: Carpeta para utilidades.
        -   `__init__.py`
-   `requirements.txt`: Dependencias del proyecto.
-   `README.md`: Documentación del proyecto.

## Requerimientos 
- python >= 3.9 < 3.12
- pip
- venv de python
- Apache

## Instalación

Asegúrate de cumplir con los requerimientos antes de empezar.

1. Crear una carpeta con el nombre del proyecto.
2. Realiza la instalación de TTS y de TTS-Service dentro del misma carpeta.

### Instalación TTS

1.  Clona el repositorio de TTS (Para poder modificar o entrenar modelos propios)
```bash
git clone https://github.com/coqui-ai/TTS
```

2.  Accede a la carpeta del proyecto.
```bash
cd TTS
```

3.  Genera un espacio virtual.
```bash
python -m venv tts_service
#or 
python3 -m venv tts_service
```

4. Actualiza pip.
```bash
pip install --upgrade pip setuptools wheel
```

5.  Ejecuta el siguiente comando para instalar las dependencias:
```bash
pip install -e .[all,dev,notebooks]
```

### Instalación TTS
1.  Clona el repositorio TTS-Service.

```bash
git clone https://github.com/ccmarin14/TTS-Service.git
```

2.  Accede a la carpeta del proyecto.

```bash
cd TTS-Service
```
3.  Genera un espacio virtual.

```bash
python -m venv tts_service
#or 
python3 -m venv tts_service
```

4. Accede al entorno virtual.

```bash
#Windows
tts_service\Scripts\activate

#Linux
source tts_service/bin/activate
```

5. Actualiza pip.

```bash
pip install --upgrade pip setuptools wheel
```

6.  Ejecuta el siguiente comando para instalar las dependencias:

```bash
pip install -r requirements.txt
```

## Ejecutar el Servicio
Para iniciar el servicio, ejecuta el siguiente comando en la terminal desde la raíz del proyecto:

```bash
uvicorn app.main:app --reload
```

Accede a la aplicación en `http://{direccion o nombre}:8000`.

##Documentación Automática
FastAPI proporciona documentación automática que puede ser accedida en:

-   Swagger UI: `http://{direccion o nombre}:8000/docs`
-   ReDoc: `http://{direccion o nombre}:8000/redoc`

## Uso del Servicio
Para utilizar el servicio de TTS, realiza una solicitud POST a la ruta `/tts/` con el siguiente cuerpo en formato JSON:

```json
{
  "text": "Texto que deseas convertir a audio.",
  "model": 2
}
```

**Respuesta Exitosa**\
Si la síntesis de audio es exitosa, recibirás una respuesta como la siguiente:

```json
{
  "message": "Audio synthesized successfully",
  "audio_path": "app/resources/audio.wav"
}
```

## Mejores Prácticas

-   Validación: Asegúrate de validar todas las entradas utilizando Pydantic.
-   Manejo de Errores: Implementa manejo de errores adecuado con excepciones de FastAPI.
-   Documentación: Aprovecha la generación automática de documentación de FastAPI.