import os
import io
import zipfile
from fastapi import UploadFile
from typing import Dict, List

from app.models.information_model import InformationModel
from app.services.storage.file_service import FileService

class ZipService:
    UPLOAD_DIR = "app/resources/uploads"
    ALLOWED_EXTENSIONS = {'.mp3'}

    async def validate_zip_file(self, zip: UploadFile) -> bool:
        """
        Valida que el archivo ZIP no este vacio y que su contenido sean audios con extensiones permitidas.

        Args:
            zip (UploadFile): Archivo zip.

        Returns:
            bool: True si el archivo es un ZIP válido, en caso contrario lanza una excepción ValueError
        """
        try:
            # Leer el contenido del archivo
            content = await zip.read()
            # Crear un objeto BytesIO para trabajar con el contenido en memoria
            zip_bytes = io.BytesIO(content)

            with zipfile.ZipFile(zip_bytes) as zip_ref:
                file_list = zip_ref.namelist()
                
                # Verificar que el ZIP no esté vacío
                if not file_list:
                    raise ValueError("El archivo ZIP está vacío")

                # Validar extensiones permitidas
                for file_name in file_list:
                    ext = os.path.splitext(file_name)[1].lower()
                    if ext not in self.ALLOWED_EXTENSIONS:
                        raise ValueError(f"Extensión no permitida: {ext}")

            # Resetear el archivo para futuras lecturas
            await zip.seek(0) 
            return True
                
        except zipfile.BadZipFile:
            raise ValueError("El archivo no es un ZIP válido")
        
    # async def extract_zip(self, zip: UploadFile) -> List[str]:
    #     try:
    #         os.makedirs(self.UPLOAD_DIR, exist_ok=True)

    #         content = await zip.read()
    #         zip_bytes = io.BytesIO(content)

    #         extracted_files = []
    #         with zipfile.ZipFile(zip_bytes) as zip_ref:
    #             zip_ref.extractall(self.UPLOAD_DIR)
    #             extracted_files = zip_ref.namelist()

    #             return extracted_files

    #     except Exception as e:
    #         raise ValueError(f"Error al extraer el ZIP: {str(e)}")
        
    async def extract_zip(self, zip:UploadFile, model:InformationModel) -> List[str]:
        try:
            os.makedirs(self.UPLOAD_DIR, exist_ok=True)

            content = await zip.read()
            zip_bytes = io.BytesIO(content)

            with zipfile.ZipFile(zip_bytes) as zip_ref:
                # Obtener la lista de archivos y generar nuevos nombres
                file_list = zip_ref.namelist()
                renamed_files = self._rename_files(file_list, model)
                
                # Extraer los archivos con los nuevos nombres
                for old_name, new_name in renamed_files.items():
                    with zip_ref.open(old_name) as source:
                        content = source.read()
                        target_path = os.path.join(self.UPLOAD_DIR, new_name)
                        with open(target_path, 'wb') as target:
                            target.write(content)

                return renamed_files
                # return [os.path.join(self.UPLOAD_DIR, file_name) for file_name in extracted_files]

        except Exception as e:
            raise ValueError(f"Error al extraer el ZIP: {str(e)}")
        
    def _rename_files(self, file_list: List[str], model:InformationModel) -> Dict[str, str]:
        """
        Genera nuevos nombres para los archivos del ZIP.
        
        Args:
            file_list (List[str]): Lista de nombres originales
            model (InformationModel): Modelo para nombrar los archivos
            
        Returns:
            Dict[str, str]: Diccionario con {nombre_original: nuevo_nombre}
        """

        renamed_files = {}
        for original_name in file_list:
            filename, ext = os.path.splitext(original_name)
            audio_name = filename + model.model
            new_name = f"{FileService.generate_hash(audio_name)}{ext}";
            renamed_files[original_name] = new_name
            
        return renamed_files