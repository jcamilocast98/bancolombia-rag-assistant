import json
from typing import Optional
from src.dominio.entidades.pagina import Pagina
from src.dominio.puertos.puerto_almacenamiento import PuertoAlmacenamiento


class AdaptadorAlmacenamientoSimulado(PuertoAlmacenamiento):
    """Adaptador de almacenamiento simulado que guarda objetos tipo JSON en memoria (diccionario de Python)."""

    def __init__(self):
        self._almacenamiento = {}

    async def guardar_html_crudo(self, pagina: Pagina) -> str:
        # Crea una clave segura a partir de la url
        url_segura = str(pagina.url).replace("/", "_").replace(":", "_")
        llave = f"{url_segura}.json" # Se guarda en crudo pero estructurado (JSON)
        
        # Almacena de forma estructurada con sus metadatos
        self._almacenamiento[llave] = pagina.model_dump_json()
        return llave

    async def obtener_html_crudo(self, ruta: str) -> Optional[str]:
        # Para la etapa de indexación, desempaquetamos el JSON y devolvemos solo el HTML
        datos_json = self._almacenamiento.get(ruta)
        if not datos_json:
            return None
        
        diccionario = json.loads(datos_json)
        return diccionario.get("contenido_html")
