from typing import List
from src.dominio.entidades.chunk import Chunk
from src.dominio.puertos.puerto_bd_vectorial import PuertoBdVectorial


class AdaptadorPgVectorSimulado(PuertoBdVectorial):
    """Adaptador de la base de datos vectorial que guarda los chunks de memoria iterando sobre PgVector."""

    def __init__(self):
        self.chunks: List[Chunk] = []

    async def insertar_chunks(self, chunks_nuevos: List[Chunk]) -> None:
        # En una BD real esto haría un UPSERT / Merge basado en el chunk_id
        self.chunks.extend(chunks_nuevos)
        print(f"[Adaptador Mock PGVector] Se insertaron {len(chunks_nuevos)} chunks. Total almacenados: {len(self.chunks)}")
