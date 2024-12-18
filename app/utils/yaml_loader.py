import os
import yaml
from string import Template

class YamlLoaderMixin:
    """
    Mixin que proporciona funcionalidad para cargar archivos YAML.
    """
    def load_yaml(self, file_path: str) -> dict:
        """
        Carga un archivo YAML y devuelve su contenido como un diccionario.
        Args:
            file_path (str): Ruta del archivo YAML.
        Returns:
            dict: Contenido del archivo YAML.
        Raises:
            FileNotFoundError: Si el archivo no se encuentra o no se puede cargar.
        """
        try:
            with open(file_path, 'r') as file:
                # Lee el archivo como template
                template = Template(file.read())
                # Reemplaza las variables con valores del entorno
                yaml_content = template.safe_substitute(os.environ)
                # Carga el YAML con los valores reemplazados
                return yaml.safe_load(yaml_content)
        except Exception as e:
            raise FileNotFoundError(f"Error al cargar el archivo YAML {file_path}: {e}")
