**Servicio de TTS**

**Descripción** Este proyecto es un backend desarrollado con FastAPI, siguiendo el patrón de diseño Modelo-Vista-Controlador (MVC). Su principal objetivo es proporcionar un servicio de Text-to-Speech (TTS) que permite convertir texto en audio.

**Estructura del Proyecto** /TTS-Service

-   **app/**
    -   `__init__.py`
    -   `main.py`: Archivo principal donde se inicializa FastAPI
    -   **models/**: Carpeta para modelos de datos
        -   `__init__.py`
        -   `tts_model.py`: Definición de modelos usando Pydantic
    -   **services/**: Carpeta para la lógica del negocio
        -   `__init__.py`
        -   `tts_service.py`: Lógica para manejar TTS
    -   **controllers/**: Carpeta para controladores (rutas)
        -   `__init__.py`
        -   `tts_controller.py`: Rutas relacionadas con TTS
    -   **utils/**: Carpeta para utilidades
        -   `__init__.py`
-   `requirements.txt`: Dependencias del proyecto
-   `README.md`: Documentación del proyecto

**Instalación**

1.  Asegúrate de tener Python y pip instalados.
2.  Clona el repositorio.
3.  Accede a la carpeta del proyecto.
4.  Ejecuta el siguiente comando para instalar las dependencias:

```bash
pip install -r requirements.txt
```

**Ejecutar el Servicio** Para iniciar el servicio, ejecuta el siguiente comando en la terminal desde la raíz del proyecto:

```bash
uvicorn app.main:app --reload
```

Accede a la aplicación en `http://127.0.0.1:8000`.

**Documentación Automática** FastAPI proporciona documentación automática que puede ser accedida en:

-   Swagger UI: `http://127.0.0.1:8000/docs`
-   ReDoc: `http://127.0.0.1:8000/redoc`

**Uso del Servicio** Para utilizar el servicio de TTS, realiza una solicitud POST a la ruta `/tts/` con el siguiente cuerpo en formato JSON:

```json
{
  "text": "Texto que deseas convertir a audio."
}
```

**Respuesta Exitosa** Si la síntesis de audio es exitosa, recibirás una respuesta como la siguiente:

```json
{
  "message": "Audio synthesized successfully",
  "audio_path": "output/audio.wav"
}
```

**Errores** Si ocurre un error durante el proceso de síntesis, recibirás un mensaje de error con el código de estado correspondiente.

**Mejores Prácticas**

-   Validación: Asegúrate de validar todas las entradas utilizando Pydantic.
-   Manejo de Errores: Implementa manejo de errores adecuado con excepciones de FastAPI.
-   Documentación: Aprovecha la generación automática de documentación de FastAPI.
