import logging
import json
import asyncpg
from typing import List, Optional
from datetime import datetime

from src.domain.ports.vector_db_port import VectorDBPort
from src.domain.entities.document_chunk import DocumentChunk
from src.domain.entities.knowledge_base_stats import KnowledgeBaseStats
from src.domain.exceptions.vector_db_exceptions import VectorDBConnectionError, QueryError
from src.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)


def _parse_metadata(value) -> dict:
    """Convierte metadata_json de asyncpg (string o dict) a dict."""
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return {}
    return {}


class PgVectorAdapter(VectorDBPort):
    """
    Adaptador real para pgvector.
    Se conecta a la tabla 'chunks' existente creada por el servicio scraping-indexing.
    Usa asyncpg directamente para máximo rendimiento.
    """

    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None

    async def _get_pool(self) -> asyncpg.Pool:
        if self._pool is None:
            try:
                self._pool = await asyncpg.create_pool(
                    settings.database_url,
                    min_size=2,
                    max_size=10,
                )
                logger.info("[pgvector] Pool de conexiones creado exitosamente.")
            except Exception as e:
                raise VectorDBConnectionError(f"No se pudo conectar a PostgreSQL: {e}")
        return self._pool

    async def search_by_text(self, query: str, top_k: int = 5) -> List[DocumentChunk]:
        """Búsqueda por texto usando ILIKE con ranking por relevancia."""
        pool = await self._get_pool()

        # Dividir la query en palabras clave para búsqueda flexible
        keywords = [f"%{word}%" for word in query.strip().split() if len(word) > 2]
        if not keywords:
            keywords = [f"%{query}%"]

        # Construir condiciones OR para cada palabra clave
        conditions = " OR ".join([f"content ILIKE ${i+1}" for i in range(len(keywords))])
        sql = f"""
            SELECT chunk_id, url, content, metadata_json,
                   (SELECT COUNT(*) FROM unnest(ARRAY[{','.join([f'(content ILIKE ${i+1})::int' for i in range(len(keywords))])}]) AS matches WHERE matches = 1) as relevance
            FROM chunks
            WHERE {conditions}
            ORDER BY relevance DESC, id ASC
            LIMIT {top_k}
        """

        try:
            async with pool.acquire() as conn:
                rows = await conn.fetch(sql, *keywords)
                logger.info(f"[pgvector] ILIKE search found {len(rows)} results for keywords: {keywords}")
                return [
                    DocumentChunk(
                        chunk_id=row["chunk_id"],
                        url=row["url"],
                        content=row["content"],
                        score=float(row.get("relevance", 0)),
                        metadata=_parse_metadata(row.get("metadata_json")),
                    )
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"[pgvector] Error en búsqueda por texto: {e}")
            # Fallback simple sin ranking
            try:
                simple_sql = """
                    SELECT chunk_id, url, content, metadata_json
                    FROM chunks
                    WHERE content ILIKE $1
                    LIMIT $2
                """
                async with pool.acquire() as conn:
                    rows = await conn.fetch(simple_sql, f"%{query}%", top_k)
                    return [
                        DocumentChunk(
                            chunk_id=row["chunk_id"],
                            url=row["url"],
                            content=row["content"],
                            score=1.0,
                            metadata=_parse_metadata(row.get("metadata_json")),
                        )
                        for row in rows
                    ]
            except Exception as e2:
                raise QueryError(f"Error en búsqueda de texto: {e2}")

    async def search_by_embedding(self, embedding: List[float], top_k: int = 5) -> List[DocumentChunk]:
        """Búsqueda por similitud coseno usando pgvector."""
        pool = await self._get_pool()

        # Formatear el vector como string pgvector
        vector_str = f"[{','.join(str(v) for v in embedding)}]"

        sql = """
            SELECT chunk_id, url, content, metadata_json,
                   1 - (embedding <=> $1::vector) as score
            FROM chunks
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> $1::vector
            LIMIT $2
        """

        try:
            async with pool.acquire() as conn:
                rows = await conn.fetch(sql, vector_str, top_k)
                logger.info(f"[pgvector] Vector search found {len(rows)} results")
                return [
                    DocumentChunk(
                        chunk_id=row["chunk_id"],
                        url=row["url"],
                        content=row["content"],
                        score=float(row.get("score", 0)),
                        metadata=_parse_metadata(row.get("metadata_json")),
                    )
                    for row in rows
                ]
        except Exception as e:
            raise QueryError(f"Error en búsqueda vectorial: {e}")

    async def get_chunks_by_url(self, url: str) -> List[DocumentChunk]:
        """Recupera todos los chunks de una URL, ordenados por posición."""
        pool = await self._get_pool()

        sql = """
            SELECT chunk_id, url, content, metadata_json
            FROM chunks
            WHERE url = $1
            ORDER BY id ASC
        """

        try:
            async with pool.acquire() as conn:
                rows = await conn.fetch(sql, url)
                return [
                    DocumentChunk(
                        chunk_id=row["chunk_id"],
                        url=row["url"],
                        content=row["content"],
                        metadata=_parse_metadata(row.get("metadata_json")),
                    )
                    for row in rows
                ]
        except Exception as e:
            raise QueryError(f"Error recuperando chunks para {url}: {e}")

    async def get_stats(self) -> KnowledgeBaseStats:
        """Estadísticas agregadas de la base de conocimiento."""
        pool = await self._get_pool()

        sql = """
            SELECT 
                COUNT(*) as total_chunks,
                COUNT(DISTINCT url) as total_documents,
                MAX(created_at) as last_updated,
                AVG(LENGTH(content)) as avg_chunk_length
            FROM chunks
        """

        try:
            async with pool.acquire() as conn:
                row = await conn.fetchrow(sql)
                return KnowledgeBaseStats(
                    total_chunks=row["total_chunks"],
                    total_documents=row["total_documents"],
                    last_updated=row["last_updated"],
                    avg_chunk_length=float(row["avg_chunk_length"] or 0),
                    embedding_model=settings.embedding_model,
                )
        except Exception as e:
            raise QueryError(f"Error obteniendo estadísticas: {e}")

    async def health_check(self) -> bool:
        """Verifica conectividad a PostgreSQL."""
        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception:
            return False
