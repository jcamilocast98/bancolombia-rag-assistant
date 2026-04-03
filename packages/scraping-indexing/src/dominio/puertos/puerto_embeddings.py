from abc import ABC, abstractmethod
from typing import List


class PuertoEmbeddings(ABC):
    """Puerto (interfaz) abstracto para conectar con proveedores de embeddings (ej: OpenAI)."""

    @abstractmethod
    async def generar_embeddings(self, textos: List[str]) -> List[List[float]]:
        """Genera representaciones vectoriales (embeddings) para una lista de textos."""
        pass
