import hashlib
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.configuracion.ajustes import ajustes
from src.dominio.entidades.chunk import Chunk

class SegmentadorTexto:
    """Divide el texto en fragmentos (chunks) aptos para generar vectores."""

    def __init__(self):
        self.separador = RecursiveCharacterTextSplitter(
            chunk_size=ajustes.tamano_chunk,
            chunk_overlap=ajustes.solapamiento_chunk,
            separators=["\n\n", "\n", ". ", " "]
        )

    def segmentar_texto(self, url: str, texto: str, metadatos: dict = None) -> List[Chunk]:
        """Crea chunks a partir de un único bloque de texto."""
        if metadatos is None:
            metadatos = {}

        chunks_crudos = self.separador.split_text(texto)
        chunks = []
        
        for i, texto_fragmento in enumerate(chunks_crudos):
            # Crear un ID determinista
            hash_id = hashlib.sha256(f"{url}_{i}".encode('utf-8')).hexdigest()
            chunk = Chunk(
                id_chunk=hash_id,
                url=url,
                contenido_texto=texto_fragmento,
                indice_chunk=i,
                metadatos=metadatos
            )
            chunks.append(chunk)
            
        return chunks
