import hashlib
import logging
from typing import List
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert as pg_insert
from src.dominio.entidades.chunk import Chunk
from src.dominio.puertos.puerto_bd_vectorial import PuertoBdVectorial
from src.infraestructura.persistencia.modelos import ChunkModel
from src.configuracion.ajustes import ajustes

logger = logging.getLogger(__name__)


class AdaptadorPgVector(PuertoBdVectorial):
    """
    Adaptador real de la base de datos vectorial pgvector.
    Almacena chunks con sus embeddings usando SQLAlchemy asíncrono.
    """

    def __init__(self):
        self.engine = create_async_engine(ajustes.url_base_datos, echo=False)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    @staticmethod
    def _generar_chunk_id(contenido: str) -> str:
        """Genera un hash SHA-256 del contenido para usar como chunk_id único."""
        return hashlib.sha256(contenido.encode("utf-8")).hexdigest()

    async def insertar_chunks(self, chunks: List[Chunk]) -> None:
        """
        Inserción masiva con upsert (ON CONFLICT DO UPDATE).
        Si el chunk_id ya existe, actualiza el embedding y la metadata.
        """
        if not chunks:
            return

        async with self.async_session() as session:
            async with session.begin():
                for chunk in chunks:
                    chunk_id = self._generar_chunk_id(chunk.contenido_texto)

                    valores = {
                        "chunk_id": chunk_id,
                        "url": chunk.url,
                        "content": chunk.contenido_texto,
                        "embedding": chunk.embedding,
                        "metadata_json": chunk.metadatos,
                    }

                    stmt = pg_insert(ChunkModel).values(**valores)
                    stmt = stmt.on_conflict_do_update(
                        index_elements=["chunk_id"],
                        set_={
                            "embedding": stmt.excluded.embedding,
                            "metadata_json": stmt.excluded.metadata_json,
                            "url": stmt.excluded.url,
                        },
                    )
                    await session.execute(stmt)

        logger.info(
            f"[pgvector] Insertados/actualizados {len(chunks)} chunks exitosamente."
        )
