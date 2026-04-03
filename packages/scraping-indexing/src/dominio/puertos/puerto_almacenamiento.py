from abc import ABC, abstractmethod
from typing import Optional

from src.dominio.entidades.pagina import Pagina


class PuertoAlmacenamiento(ABC):
    """Puerto (interfaz) abstracto para operaciones de guardado de archivos."""

    @abstractmethod
    async def guardar_html_crudo(self, pagina: Pagina) -> str:
        """
        Guarda el archivo HTML crudo (ej: en S3 o MinIO).
        Retorna la ruta o llave ('key') donde se guardó.
        """
        pass

    @abstractmethod
    async def obtener_html_crudo(self, ruta: str) -> Optional[str]:
        """
        Recupera el contenido HTML crudo desde el almacenamiento dada la ruta o llave.
        """
        pass
