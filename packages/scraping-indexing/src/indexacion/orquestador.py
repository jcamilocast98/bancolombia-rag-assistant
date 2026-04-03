from typing import Optional
from src.dominio.entidades.pagina import Pagina
from src.dominio.puertos.puerto_almacenamiento import PuertoAlmacenamiento
from src.indexacion.limpiador_datos import LimpiadorDatos
from src.indexacion.segmentador_texto import SegmentadorTexto
from src.indexacion.generador_embeddings import GeneradorEmbeddings
from src.indexacion.acceso_bd_vectorial import AccesoBdVectorial


class OrquestadorIndexacion:
    """Orquesta la tubería de indexación: Lectura -> Limpieza -> Chunks -> Embeddings -> Guardar."""
    
    def __init__(
        self,
        puerto_almacenamiento: PuertoAlmacenamiento,
        limpiador: LimpiadorDatos,
        segmentador: SegmentadorTexto,
        generador_embeddings: GeneradorEmbeddings,
        acceso_bd: AccesoBdVectorial
    ):
        self.almacenamiento = puerto_almacenamiento
        self.limpiador = limpiador
        self.segmentador = segmentador
        self.generador = generador_embeddings
        self.acceso_bd = acceso_bd

    async def procesar_documento(self, ruta_almacenamiento: str, url_origen: str, metadatos: dict = None) -> bool:
        """
        Lee el documento en crudo desde el almacenamiento y lo transforma hasta ingresarlo a la BD abstracta.
        """
        html_crudo = await self.almacenamiento.obtener_html_crudo(ruta_almacenamiento)
        if not html_crudo:
            print(f"[Indexación] Archivo no encontrado en almacenamiento: {ruta_almacenamiento}")
            return False

        # 1. Limpieza
        texto_limpio = self.limpiador.limpiar_html(html_crudo)
        if not texto_limpio or len(texto_limpio) < 10:
            print(f"[Indexación] Ignorando contenido corto o vacío para: {url_origen}")
            return False
            
        print(f"[Indexación] Limpieza de {url_origen}. Caracteres extraídos: {len(texto_limpio)}.")

        # 2. Segmentación en chunks
        chunks = self.segmentador.segmentar_texto(url=url_origen, texto=texto_limpio, metadatos=metadatos)
        print(f"[Indexación] Generados {len(chunks)} chunks para {url_origen}.")

        # 3. Vectorización (Embeddings)
        chunks = await self.generador.incrustar_chunks(chunks)
        print(f"[Indexación] Embeddings (vectores) asignados a {len(chunks)} chunks.")

        # 4. Guardar en Base de Datos Vectorial
        await self.acceso_bd.guardar_chunks(chunks)
        print(f"[Indexación] Agregados {len(chunks)} chunks exitosamente a la base de datos.")
        
        return True
