from abc import ABC, abstractmethod
from typing import List

from src.dominio.entidades.chunk import Chunk


class PuertoBdVectorial(ABC):
    """Puerto (interfaz) abstracto para insertar chunks vectorizados en la BD (ej: pgvector)."""

    @abstractmethod
    async def insertar_chunks(self, chunks: List[Chunk]) -> None:
        """Inserción masiva (bulk insert) de una lista de chunks. Debe manejar la deduplicación basada en la URL y el índice."""
        pass
