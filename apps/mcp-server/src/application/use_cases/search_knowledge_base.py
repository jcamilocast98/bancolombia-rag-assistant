import logging
from typing import List
from src.domain.ports.vector_db_port import VectorDBPort
from src.domain.ports.embedding_port import EmbeddingPort
from src.domain.entities.search_result import SearchResult
from src.domain.entities.document_chunk import DocumentChunk
from src.domain.exceptions.embedding_exceptions import EmbeddingGenerationError

logger = logging.getLogger(__name__)


class SearchKnowledgeBase:
    """Caso de uso: búsqueda semántica en la base de conocimiento."""

    def __init__(self, vector_db: VectorDBPort, embedding_adapter: EmbeddingPort):
        self.vector_db = vector_db
        self.embedding_adapter = embedding_adapter

    async def execute(self, query: str, top_k: int = 5) -> SearchResult:
        if not query or not query.strip():
            return SearchResult(query=query, chunks=[], total_results=0)

        chunks: List[DocumentChunk] = []
        search_method = "text"

        # Intentar búsqueda vectorial primero
        try:
            embedding = await self.embedding_adapter.generate_query_embedding(query)
            chunks = await self.vector_db.search_by_embedding(embedding, top_k)
            search_method = "vector"
            logger.info(f"[SearchKB] Búsqueda vectorial exitosa: {len(chunks)} resultados")
        except (EmbeddingGenerationError, Exception) as e:
            logger.warning(f"[SearchKB] Fallback a texto. Razón: {e}")
            chunks = await self.vector_db.search_by_text(query, top_k)
            search_method = "text"

        return SearchResult(
            query=query,
            chunks=chunks,
            total_results=len(chunks),
            search_method=search_method,
        )
