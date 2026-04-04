from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.document_chunk import DocumentChunk
from ..entities.knowledge_base_stats import KnowledgeBaseStats


class VectorDBPort(ABC):
    """Puerto abstracto para la base de datos vectorial."""

    @abstractmethod
    async def search_by_text(self, query: str, top_k: int = 5) -> List[DocumentChunk]:
        """Búsqueda por coincidencia de texto (fallback)."""
        pass

    @abstractmethod
    async def search_by_embedding(self, embedding: List[float], top_k: int = 5) -> List[DocumentChunk]:
        """Búsqueda por similitud coseno con pgvector."""
        pass

    @abstractmethod
    async def get_chunks_by_url(self, url: str) -> List[DocumentChunk]:
        """Obtiene todos los chunks de una URL específica, ordenados."""
        pass

    @abstractmethod
    async def get_stats(self) -> KnowledgeBaseStats:
        """Retorna estadísticas agregadas de la base de conocimiento."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Verifica la conexión a la base de datos."""
        pass
