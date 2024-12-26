# Servicio de Text-to-Speech (TTS)

![Docker Pulls](https://img.shields.io/docker/pulls/cristianmaringma/tts-service?style=flat-square)
![Docker Image Size](https://img.shields.io/docker/image-size/cristianmaringma/tts-service)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/ccmarin14/tts-service)

## Descripción

Servicio API REST construido con FastAPI que convierte texto a voz utilizando el servicio Play.ht. El sistema implementa cacheo de audios, almacenamiento en AWS S3 y registro en base de datos MySQL.

## Características Principales

-   Conversión de texto a voz mediante Play.ht API
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

## Instalación y Uso

### 1. Usando Docker (Recomendado)

1. Crea un archivo .env con las siguientes variables (o descarga el ejemplo):
```.env
# API Credentials
API_USER_ID=your_user_id
API_AUTH_TOKEN=your_auth_token

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
    input_text TEXT NOT NULL,
    language VARCHAR(50) NOT NULL,
    gender CHAR(1) NOT NULL,
    model VARCHAR(100) NOT NULL,
    file_url VARCHAR(255) NOT NULL,
    audio_hash VARCHAR(64) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
git clone https://github.com/ccmarin14/TTS-Service.git
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
│   ├── controllers/
│   │  └── tts_controller.py    # Endpoints de la API
│   ├── models/
│   │  └── tts_model.py        # Modelos de datos
│   ├── services/
│   │  ├── tts_service.py      # Lógica principal de TTS
│   │  ├── file_service.py     # Gestión de archivos
│   │  ├── s3_service.py       # Integración con AWS S3
│   │  └── db_service.py       # Operaciones con MySQL
│   ├── data/
│   │  └── voices_config.yaml  # Configuración de voces
│   └── main.py                 # Inicialización de FastAPI
├── config.yaml                 # Configuración general
└── requirements.txt           # Dependencias del proyecto
```

## Uso de la API

### Convertir Texto a Voz

```bash
POST /tts/
```

### Payload:

```json
{
  "text": "Texto a convertir",
  "language": "es-ES",
  "gender": "F",
  "model": "Carmen"
}
```

### Respuesta:

```json
{
  "message": "Audio synthesized successfully",
  "audio_path": "https://tu-bucket.s3.amazonaws.com/audios/hash.mp3"
}
```

### Obtener Modelos Disponibles

```bash
GET /models/
```

## Flujo de la aplicación
```mermaid
graph TD
    A[Cliente] -->|POST /tts/| B[TTSController]
    B -->|Verifica hash| C[DBService]
    C -->|Si existe| D[Retorna URL existente]
    C -->|Si no existe| E[TTSService]
    E -->|Selecciona voz| G[Configuración YAML]
    G -->|Genera audio| H[Play.ht API]
    H -->|Audio generado| I[FileService]
    I -->|Archivo temporal| J[S3Service]
    J -->|Sube archivo| K[AWS S3]
    K -->|Obtiene URL| L[DBService]
    L -->|Guarda metadata| M[MySQL]
    M -->|URL del audio| N[Respuesta al cliente]
    D -->M
```

## Versiones Disponibles

- `latest`: Última versión estable
- `1.0.0`: Primera versión estable
- `1.0.0-alpine`: Versión ligera basada en Alpine Linux

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
©2024, GMA Digital - Todos los derechos reservados.