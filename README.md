# Servicio de Text-to-Speech (TTS)

![Docker Pulls](https://img.shields.io/docker/pulls/cristianmaringma/tts-service?style=flat-square)
![Docker Image Size](https://img.shields.io/docker/image-size/cristianmaringma/tts-service)

## Descripción

Servicio API REST construido con FastAPI que convierte texto a voz utilizando el servicios en linea. El sistema implementa cacheo de audios, almacenamiento en AWS S3 y registro en base de datos MySQL.

## Características Principales

-   Conversión de texto a voz mediante TTS online
-   Soporte multiidioma (Inglés y Español)
-   Voces masculinas y femeninas
-   Almacenamiento en AWS S3
-   Cacheo de audios generados
-   Base de datos MySQL para metadata
-   Configuración mediante archivos YAML

## Requerimientos
-   Python >= 3.9 < 3.12
-   MySQL
-   Cuenta AWS (S3)
-   Cuenta Play.ht
-   Cuenta Voicemaker.in

## Instalación y Uso

### 1. Usando Docker (Recomendado)

1. Crea un archivo .env con las siguientes variables (o descarga el ejemplo):
```.env
# API Credentials
VOICEMAKER_BEARER=Bearer xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
PLAYHT_API_USER_ID=your_user_id
PLAYHT_API_AUTH_TOKEN=your_auth_token

# AWS Credentials
AWS_ACCESS_KEY=your_access_key
AWS_SECRET_KEY=your_secret_key
AWS_REGION=your_region
AWS_BUCKET=your_bucket
AWS_URL=your_s3_url

# Database Credentials
DB_HOST=your_host
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database 

# CORS Settings (comma-separated URLs)
CORS_ORIGINS=["http://localhost:3000","http://localhost:5500","http://127.0.0.1:5500"]
```

2. Crea la tabla en tu base de datos MySQL:
```sql
CREATE TABLE generated_audios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    original_text TEXT,
    input_text TEXT NOT NULL,
    information_id INT DEFAULT NULL,
    file_url VARCHAR(255) NOT NULL,
    audio_hash VARCHAR(64) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE information_audios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  voice_name VARCHAR(255) NOT NULL,
  `language` VARCHAR(45) NOT NULL,
  gender ENUM('M','F') NOT NULL,
  `type` ENUM('robot','adult','child') NOT NULL,
  platform VARCHAR(45) DEFAULT NULL,
  model VARCHAR(500) NOT NULL,  
);
```

3. Puedes ejecutar el servicio de dos formas:

#### Opción A: Usando Docker directamente
```bash
docker pull cristianmaringma/tts-service:latest
docker run -p 8000:8000 --env-file .env cristianmaringma/tts-service:latest
```

#### Opción B: Usando Docker Compose
1. Crea un archivo docker-compose.yml:
```yaml
services:
  tts-service:
    image: cristianmaringma/tts-service:latest
    ports:
      - "8000:8000"
    env_file:
      - .env
```

2. Inicia el servicio:
```bash
docker-compose up -d
```

### 2. Instalación Local (Para Desarrollo)

1. Clona el repositorio:
```bash
git clone https://gl.master2000.net/cristianmarin/TTS-Service
```

2. Crea y configura tu archivo .env:
```bash
cp .env.example .env
# Edita .env con tus credenciales
```

3. Inicia el servicio:
```bash
docker-compose up -d
```

## Estructura del Proyecto
```
/TTS-Service
├── app/
│   ├── controllers/
│   │   └── tts_controller.py     # Endpoints de la API
│   ├── models/
│   │   ├── tts_model.py          # Modelos para requests TTS
│   │   └── information_model.py  # Modelos para voces
│   ├── providers/                # Proveedores TTS
│   │   ├── base.py               # Clase base para providers
│   │   ├── playht.py             # Proveedor Play.ht
│   │   ├── polly.py              # Proveedor Amazon Polly
│   │   └── voicemaker.py         # Proveedor Voicemaker
│   ├── resources/                # Recursos
│   │   ├── audios                # Carpeta temporal de audios
│   │   └── uploads               # Carpeta temporal para audios cargados
│   ├── services/
│   │   ├── container_service.py  # Contenedor de servicios
│   │   ├── database/
│   │   │   └── db_service.py     # Operaciones con MySQL
│   │   ├── storage/
│   │   │   ├── file_service.py   # Gestión de archivos
│   │   │   └── s3_service.py     # Integración con AWS S3
│   │   ├── tts/
│   │   │   └── tts_service.py    # Servicio principal TTS
│   │   ├── container_service.py  # Servicio para agrupar los servicios
│   │   └── zip_service.py        # Servicio para descomprimir archivo zip y preparar audios.
│   ├── utils/
│   │   └── yaml_loader.py        # Utilidad para YAML
│   ├── validators/
│   │   └── tts_validator.py      # Validación de requests
│   ├── main.py                   # Inicialización de FastAPI
│   └── static_files.py           # Montaje de la carpeta de recursos
├── config.yaml                   # Configuración general
└── requirements.txt              # Dependencias del proyecto
```

## Uso de la API
### 1. Convertir Texto a Voz por Nombre
```bash
POST /tts/by-name/
```

#### Descripción
Genera un archivo de audio utilizando el nombre específico de un modelo de voz.

#### Parámetros del Request
```json
{
  "text": "Texto original a convertir",
  "read": "Texto que se leerá",
  "language": "es-ES",
  "model": "Carmen"
}
```

#### Respuesta Exitosa
```json
{
  "message": "Audio sintetizado correctamente",
  "audio_path": "https://bucket.s3.amazonaws.com/audios/hash.mp3"
}
```

#### Errores Comunes
```json
{
  "detail": "Información no encontrada para el lenguage:'es-ES' y para el nombre del modelo:'Carmen'"
}
```

#### Ejemplo de Uso con cURL
```bash
curl -X 'POST' \
  'http://localhost:8000/tts/by-name/' \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "Texto original a convertir",
    "read": "Texto que se leerá",
    "language": "es-ES",
    "model": "Carmen"
}'
```

#### Notas
- El campo `read` es opcional, si no se proporciona se usará el valor de `text`
- El modelo debe existir para el idioma especificado
- El texto se limpiará automáticamente de espacios extra

### 2. Convertir Texto a Voz por ID
```bash
POST /tts/{model_id}
```
#### Descripción
Genera un archivo de audio utilizando el ID de un modelo de voz.

#### Parámetros de Ruta
- `model_id` (integer, required): ID del modelo de voz a utilizar

#### Parámetros del Request
```json
{
  "text": "Texto original a convertir",
  "read": "Texto que se leerá"
}
```

#### Respuesta Exitosa
```json
{
  "message": "Audio sintetizado correctamente",
  "audio_path": "https://bucket.s3.amazonaws.com/audios/hash.mp3"
}
```

#### Errores Comunes
```json
{
  "detail": "Modelo con el id:123 no encontrado"
}
```

#### Ejemplo de Uso con cURL
```bash
curl -X 'POST' \
  'http://localhost:8000/tts/1' \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "Texto original a convertir",
    "read": "Texto que se leerá"
}'
```

#### Notas
- El ID del modelo debe existir en la base de datos
- Se añadirá un punto final al texto si no lo tiene
- El audio generado se cachea para futuras solicitudes

### 3. Convertir Texto con Parámetros Opcionales
```bash
POST /tts/optional/
```
#### Descripción
Genera un archivo de audio especificando características opcionales del modelo de voz.

#### Parámetros del Request
```json
{
  "text": "Texto original a convertir",
  "read": "Texto que se leerá",
  "language": "es-ES",
  "gender": "F",
  "type": "adult"
}
```

#### Respuesta Exitosa
```json
{
  "message": "Audio sintetizado correctamente",
  "audio_path": "https://bucket.s3.amazonaws.com/audios/hash.mp3"
}
```

#### Errores Comunes
```json
{
  "detail": "Información no encontrada para el lenguage:'es-ES' para el genero:'F' y del tipo:'adult'"
}
```

#### Ejemplo de Uso con cURL
```bash
curl -X 'POST' \
  'http://localhost:8000/tts/optional/' \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "Texto original a convertir",
    "read": "Texto que se leerá",
    "language": "es-ES",
    "gender": "F",
    "type": "adult"
}'
```

#### Notas
- Se seleccionará el primer modelo que coincida con los parámetros
- Los valores permitidos para `type` son: "adult", "child", "robot"
- Los valores permitidos para `gender` son: "M", "F"

### 4. Cargar Audios para un Modelo de Voz
```bash
POST /tts/upload-zip/{model_id}
```

#### Descripción
Permite cargar un archivo ZIP que contiene archivos de audio MP3 y los asocia a un modelo de voz específico. Los archivos serán renombrados y almacenados automáticamente.

#### Parámetros de Ruta
- `model_id` (integer, required): ID del modelo de voz al que se asociarán los audios

#### Parámetros del Request
- `file` (file, required): Archivo ZIP que contiene los audios MP3
  - Content-Type: multipart/form-data
  - Formato: ZIP
  - Extensiones permitidas dentro del ZIP: .mp3

#### Respuesta Exitosa
```json
{
  "message": "Archivo zip cargado correctamente",
  "extracted_files": {
    "original_name.mp3": "hash_generado.mp3",
    "otro_audio.mp3": "otro_hash_generado.mp3"
  }
}
```

#### Errores Comunes
```json
{
  "detail": "Modelo con el id:123 no encontrado"
}
```

```json
{
  "detail": "El archivo ZIP está vacío"
}
```

```json
{
  "detail": "Extensión no permitida: .wav"
}
```

#### Ejemplo de Uso con cURL
```bash
curl -X 'POST' \
  'http://localhost:8000/tts/upload-zip/1' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@audios.zip'
```

#### Notas
- El archivo ZIP debe contener solo archivos MP3
- Los archivos serán renombrados usando un hash único basado en su contenido
- Los archivos duplicados (mismo contenido) serán ignorados
- El tamaño máximo del archivo ZIP depende de la configuración del servidor

### 5. Crear Nuevo Modelo de Voz
```bash
POST /models/
```
#### Descripción
Crea un nuevo modelo de voz en el sistema.

#### Parámetros del Request
```json
{
  "voice_name": "Nueva Voz",
  "language": "es-ES",
  "gender": "F",
  "type": "adult",
  "platform": "polly",
  "model": "Lucia"
}
```

#### Respuesta Exitosa
```json
{
  "message": "Modelo creado correctamente",
  "model": {
    "id": 3,
    "voice_name": "Nueva Voz",
    "language": "es-ES",
    "gender": "F",
    "type": "adult",
    "platform": "polly",
    "model": "Lucia"
  }
}
```

#### Errores Comunes
```json
{
  "detail": "Ya existe un modelo con el nombre: Nueva Voz"
}
```

#### Ejemplo de Uso con cURL
```bash
curl -X 'POST' \
  'http://localhost:8000/models/' \
  -H 'Content-Type: application/json' \
  -d '{
    "voice_name": "Nueva Voz",
    "language": "es-ES",
    "gender": "F",
    "type": "adult",
    "platform": "polly",
    "model": "Lucia"
}'
```

#### Notas
- El nombre de la voz debe ser único
- La plataforma debe ser una de las soportadas: "polly", "playht", "voicemaker"
- Los modelos creados están disponibles inmediatamente

### 6. Obtener Modelos Disponibles
```bash
GET /models/
```
#### Descripción
Retorna la lista de todos los modelos de voz disponibles en el sistema.

#### Respuesta Exitosa
```json
[
  {
    "id": 1,
    "voice_name": "Carmen",
    "language": "es-ES",
    "gender": "F",
    "type": "adult",
    "platform": "playht",
    "model": "s3://voice-cloning-zero-shot/d9ff78ba-d016"
  },
  {
    "id": 2,
    "voice_name": "Lucia",
    "language": "es-ES",
    "gender": "F",
    "type": "adult",
    "platform": "polly",
    "model": "Lucia"
  }
]
```

#### Errores Comunes
```json
{
  "detail": "Error al cargar los modelos"
}
```

#### Ejemplo de Uso con cURL
```bash
curl -X 'GET' \
  'http://localhost:8000/models/' \
  -H 'accept: application/json'
```

#### Notas
- Los modelos se devuelven ordenados por ID
- Incluye todos los modelos activos en el sistema
- La respuesta está organizada por plataforma y características

## Notas Generales
- Todos los endpoints requieren autenticación mediante token
- Los audios generados se almacenan en S3 y se cachean
- El límite de tamaño para archivos ZIP es de 100MB
- Las respuestas de error siguen el formato estándar de FastAPI
- Los tiempos de respuesta dependen del proveedor TTS seleccionado
- Se recomienda usar HTTPS en producción

## Flujo de la aplicación
```mermaid
graph TD
    %% Flujo común para sintetizar audio
    A[Cliente] -->|POST| B[TTSController]
    B -->|Valida request| C[TTSValidator]
    C -->|Verifica cache| D[DBService]
    D -->|Si existe| E[Retorna URL existente]
    D -->|Si no existe| F[TTSService]
    F -->|Selecciona provider| G{Provider Type}
    G -->|PlayHT| H[PlayHT Provider]
    G -->|Polly| I[Polly Provider]
    G -->|Voicemaker| J[Voicemaker Provider]
    H & I & J -->|Audio generado| K[FileService]
    K -->|Archivo temporal| L[S3Service]
    L -->|Sube archivo| M[AWS S3]
    M -->|Obtiene URL| N[DBService]
    N -->|Guarda metadata| O[MySQL]
    O -->|URL del audio| P[Cliente]
    E -->P

    %% Flujo para cargar ZIP
    AA[Cliente] -->|POST ZIP| BB[TTSController]
    BB -->|Valida modelo| CC[DBService]
    CC -->|Si existe| DD[ZipService]
    DD -->|Valida ZIP| EE{Es válido?}
    EE -->|No| FF[Error formato]
    EE -->|Sí| GG[Extrae y renombra]
    GG -->|Archivos procesados| HH[TTSService]
    HH -->|Por cada archivo| II[FileService]
    II -->|Sube a S3| JJ[S3Service]
    JJ -->|URLs| KK[DBService]
    KK -->|Guarda metadata| LL[MySQL]
    LL -->|Lista de archivos| MM[Cliente]
    FF -->MM

    %% Flujo para obtener modelos
    Q[Cliente] -->|GET /models| R[TTSController]
    R -->|Obtiene modelos| S[DBService]
    S -->|Lista de modelos| T[Cliente]

    %% Flujo para crear modelo
    U[Cliente] -->|POST /models| V[TTSController]
    V -->|Verifica duplicado| W[DBService]
    W -->|Si no existe| X[DBService Save]
    X -->|Modelo creado| Y[Cliente]
    W -->|Si existe| Z[Error Duplicado]
    Z -->Y
```

## Versiones Disponibles
- `latest`: Última versión estable
- `1.0.0`: Primera versión estable
- `2.0.3`: Segunda versión estable que permite trabajar con multiples TTS en línea
- `2.1.0`: Segunda versión estable, con la posibilidad de cargar audios relacionados a un modelo.

## Mantenimiento
### Actualización de la Imagen
Para actualizar a la última versión:
```bash
docker pull cristianmaringma/tts-service:latest
```

### Logs y Monitoreo
```bash
# Ver logs del contenedor
docker logs tts-service

# Ver estadísticas de uso
docker stats tts-service
```

## Documentación API
-   Swagger UI: http://localhost:8000/docs
-   ReDoc: http://localhost:8000/redoc

## Soporte
Si encuentras algún problema o tienes alguna sugerencia, por favor:
1. Revisa los issues existentes en GitHub
2. Abre un nuevo issue si es necesario
3. Contacta al equipo de mantenimiento

## Licencia
©2025, GMA Digital - Todos los derechos reservados.