import boto3
from botocore.exceptions import NoCredentialsError

class S3Service:
    def __init__(self, aws_config: dict):
        """
        Inicializa el cliente S3 con la configuración proporcionada.
        :param aws_config: Diccionario con la configuración de AWS (credentials, bucket, region, etc.)
        """
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_config['access_key_id'],
            aws_secret_access_key=aws_config['secret_access_key'],
            region_name=aws_config['region'],
            endpoint_url=aws_config['url']
        )
        self.bucket_name = aws_config['bucket']

    def upload_audio(self, file_path, object_name):
        """Sube un archivo de audio a un bucket de S3."""
        try:
            destination_path = f"audios/{object_name}.mp3"
            self.s3_client.upload_file(file_path, self.bucket_name, destination_path)
            
            return(f"{self.s3_client.meta.endpoint_url}/{self.bucket_name}/{destination_path}")  # Retorna la URL del archivo subido
        except FileNotFoundError:
            raise Exception(f"El archivo {file_path} no fue encontrado.")
        except NoCredentialsError:
            raise Exception("No se encontraron las credenciales de AWS.")
        except Exception as e:
            raise Exception(f"Error al subir el archivo a S3: {str(e)}")