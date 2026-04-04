"""
Script de re-indexación de embeddings con Gemini.
Lee los chunks existentes de PostgreSQL y les genera embeddings
con gemini-embedding-001 (reducido a 768 dimensiones).

Uso:
    python reindexar_embeddings.py
"""
import asyncio
import asyncpg
import os
import sys
import logging
from google import genai
from google.genai import types

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Configuración
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://raguser:changeme@localhost:5432/bancolombia_rag"
)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
EMBEDDING_MODEL = "gemini-embedding-001"
OUTPUT_DIMS = 768
BATCH_SIZE = 50


async def main():
    if not GEMINI_API_KEY:
        logger.error("Falta GEMINI_API_KEY. Configúrala como variable de entorno.")
        sys.exit(1)

    client = genai.Client(api_key=GEMINI_API_KEY)

    logger.info(f"Conectando a PostgreSQL...")
    pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=5)

    async with pool.acquire() as conn:
        total = await conn.fetchval("SELECT count(*) FROM chunks")
        logger.info(f"Total chunks: {total}")

        rows = await conn.fetch("SELECT id, content FROM chunks ORDER BY id ASC")

    logger.info(f"Re-indexando {len(rows)} chunks con {EMBEDDING_MODEL} ({OUTPUT_DIMS} dims)...")

    updated_count = 0
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        texts = [row["content"] for row in batch]
        ids = [row["id"] for row in batch]

        logger.info(f"  Lote {i // BATCH_SIZE + 1}: {len(batch)} chunks (IDs {ids[0]}-{ids[-1]})")

        try:
            result = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=texts,
                config=types.EmbedContentConfig(output_dimensionality=OUTPUT_DIMS),
            )
            embeddings = [emb.values for emb in result.embeddings]
            await asyncio.sleep(2) # Evitar rate limits
        except Exception as e:
            logger.error(f"  Error generando embeddings: {e}")
            if "429" in str(e):
                logger.info("  Esperando 60 segundos por rate limit...")
                await asyncio.sleep(60)
                # Reintentar una vez
                try:
                    result = client.models.embed_content(
                        model=EMBEDDING_MODEL,
                        contents=texts,
                        config=types.EmbedContentConfig(output_dimensionality=OUTPUT_DIMS),
                    )
                    embeddings = [emb.values for emb in result.embeddings]
                except Exception as e2:
                    logger.error(f"  Fallo en el reintento: {e2}")
                    continue
            else:
                continue

        logger.info(f"  Embeddings generados: {len(embeddings)} vectores de {len(embeddings[0])} dims")

        async with pool.acquire() as conn:
            for chunk_id, embedding in zip(ids, embeddings):
                vector_str = f"[{','.join(str(v) for v in embedding)}]"
                await conn.execute(
                    "UPDATE chunks SET embedding = $1::vector WHERE id = $2",
                    vector_str,
                    chunk_id,
                )
            updated_count += len(embeddings)

        logger.info(f"  Actualizados {updated_count}/{len(rows)} chunks")

    # Verificación final
    async with pool.acquire() as conn:
        con_embedding = await conn.fetchval("SELECT count(*) FROM chunks WHERE embedding IS NOT NULL")
        dims = await conn.fetchval("SELECT vector_dims(embedding) FROM chunks WHERE embedding IS NOT NULL LIMIT 1")
    
    logger.info("=" * 60)
    logger.info(f"Re-indexación completada")
    logger.info(f"   Chunks con embedding: {con_embedding}/{total}")
    logger.info(f"   Dimensiones: {dims}")
    logger.info("=" * 60)

    await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
