from typing import List
from src.dominio.entidades.chunk import Chunk
from src.dominio.puertos.puerto_bd_vectorial import PuertoBdVectorial

class AccesoBdVectorial:
    """Proporciona abstracción parar gestionar las operaciones contra PgVector."""

    def __init__(self, puerto_bd: PuertoBdVectorial):
        self.puerto_bd = puerto_bd

    async def guardar_chunks(self, chunks: List[Chunk]) -> None:
        """Guarda la lista de chunks generados en la base de datos."""
        if not chunks:
            return
        await self.puerto_bd.insertar_chunks(chunks)
