from abc import ABC, abstractmethod
from typing import List


class EmbeddingPort(ABC):
    """Puerto abstracto para generación de embeddings de las queries."""

    @abstractmethod
    async def generate_query_embedding(self, text: str) -> List[float]:
        """Genera el vector embedding de un texto de consulta."""
        pass
