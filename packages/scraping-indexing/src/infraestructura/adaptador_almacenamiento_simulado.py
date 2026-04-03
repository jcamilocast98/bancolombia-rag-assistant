from typing import Optional
from src.dominio.entidades.pagina import Pagina
from src.dominio.puertos.puerto_almacenamiento import PuertoAlmacenamiento


class AdaptadorAlmacenamientoSimulado(PuertoAlmacenamiento):
    """Adaptador de almacenamiento simulado que guarda el HTML en memoria (diccionario de Python)."""

    def __init__(self):
        self._almacenamiento = {}

    async def guardar_html_crudo(self, pagina: Pagina) -> str:
        # Crea una clave segura a partir de la url
        url_segura = str(pagina.url).replace("/", "_").replace(":", "_")
        llave = f"{url_segura}.html"
        self._almacenamiento[llave] = pagina.contenido_html
        return llave

    async def obtener_html_crudo(self, ruta: str) -> Optional[str]:
        return self._almacenamiento.get(ruta)
