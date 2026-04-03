from src.dominio.entidades.pagina import Pagina
from src.dominio.puertos.puerto_almacenamiento import PuertoAlmacenamiento
from src.scraping.extractor_contenido import ExtractorContenido


class GestorAlmacenamiento:
    """Orquesta la extracción de contenido y su guardado en crudo."""
    
    def __init__(self, puerto_almacenamiento: PuertoAlmacenamiento):
        self.puerto_almacenamiento = puerto_almacenamiento
        self.extractor = ExtractorContenido()

    async def procesar_y_guardar(self, url: str) -> str:
        """
        Descarga la URL, crea la Pagina y delega el guardado al PuertoAlmacenamiento.
        Retorna la ruta o llave ('key') en caso de éxito.
        """
        # 1. Extraer contenido
        pagina: Pagina = await self.extractor.descargar_pagina(url)
        
        # 2. Verificar validez
        if not pagina.es_valida():
            raise ValueError(f"La página {url} no es válida (código: {pagina.codigo_estado}).")
            
        # 3. Guardar el contenido crudo (MinIO/S3)
        ruta_almacenamiento = await self.puerto_almacenamiento.guardar_html_crudo(pagina)
        return ruta_almacenamiento
