import logging
from src.domain.ports.vector_db_port import VectorDBPort
from src.domain.entities.document_chunk import DocumentChunk
from typing import List

logger = logging.getLogger(__name__)


class GetArticleByUrl:
    """Caso de uso: obtener el contenido completo de un artículo por URL."""

    def __init__(self, vector_db: VectorDBPort):
        self.vector_db = vector_db

    async def execute(self, url: str) -> dict:
        if not url or not url.strip():
            return {"error": "URL vacía", "content": "", "chunks_count": 0}

        chunks = await self.vector_db.get_chunks_by_url(url)

        if not chunks:
            return {
                "error": f"No se encontró contenido para la URL: {url}",
                "content": "",
                "url": url,
                "chunks_count": 0,
            }

        # Reconstruir el artículo completo concatenando los chunks en orden
        full_content = "\n\n".join(chunk.content for chunk in chunks)
        metadata = chunks[0].metadata if chunks else {}

        logger.info(f"[GetArticle] Recuperados {len(chunks)} chunks para {url}")

        return {
            "url": url,
            "content": full_content,
            "chunks_count": len(chunks),
            "metadata": metadata,
        }
