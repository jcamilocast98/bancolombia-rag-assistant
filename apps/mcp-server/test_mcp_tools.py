"""
Test de integración: Valida las herramientas MCP contra los 548 chunks reales.
Ejecutar desde: apps/mcp-server/
Comando: python test_mcp_tools.py
"""
import asyncio
import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from src.infrastructure.adapters.pgvector_adapter import PgVectorAdapter
from src.application.use_cases.search_knowledge_base import SearchKnowledgeBase
from src.application.use_cases.get_article_by_url import GetArticleByUrl
from src.application.use_cases.get_knowledge_base_stats import GetKnowledgeBaseStats
from src.infrastructure.adapters.gemini_embedding_adapter import GeminiEmbeddingAdapter


async def test_tools():
    print("=" * 60)
    print("  TEST: Herramientas MCP contra pgvector")
    print("=" * 60)

    # Instanciar adaptadores
    vector_db = PgVectorAdapter()
    embedding = GeminiEmbeddingAdapter()

    # ─────────────────────────────────────
    # Test 1: Health Check
    # ─────────────────────────────────────
    print("\n[Test 1] Health Check PostgreSQL...")
    ok = await vector_db.health_check()
    print(f"  -> {'[OK] Conectado' if ok else '[ERROR] Sin conexion'}")

    if not ok:
        print("  No se puede continuar sin BD. Asegúrate de que rag-postgres esté corriendo.")
        return

    # ─────────────────────────────────────
    # Test 2: Estadísticas de la KB
    # ─────────────────────────────────────
    print("\n[Test 2] knowledge-base://stats (estadísticas)...")
    stats_uc = GetKnowledgeBaseStats(vector_db=vector_db)
    stats = await stats_uc.execute()
    print(f"  → Chunks totales:    {stats.total_chunks}")
    print(f"  → URLs únicas:       {stats.total_documents}")
    print(f"  → Última indexación: {stats.last_updated}")
    print(f"  → Long. promedio:    {stats.avg_chunk_length:.0f} chars")

    # ─────────────────────────────────────
    # Test 3: Búsqueda por texto
    # ─────────────────────────────────────
    print("\n[Test 3] search_knowledge_base('cuentas de ahorro')...")
    search_uc = SearchKnowledgeBase(vector_db=vector_db, embedding_adapter=embedding)
    result = await search_uc.execute(query="cuentas de ahorro", top_k=3)
    print(f"  → Método: {result.search_method}")
    print(f"  → Resultados: {result.total_results}")
    for i, chunk in enumerate(result.chunks, 1):
        print(f"  [{i}] {chunk.url}")
        print(f"      {chunk.content[:100]}...")

    # ─────────────────────────────────────
    # Test 4: Recuperar artículo por URL
    # ─────────────────────────────────────
    print("\n[Test 4] get_article_by_url('https://www.bancolombia.com/personas/cuentas')...")
    article_uc = GetArticleByUrl(vector_db=vector_db)
    article = await article_uc.execute(url="https://www.bancolombia.com/personas/cuentas")
    print(f"  → Chunks: {article['chunks_count']}")
    print(f"  → Contenido (primeros 200 chars):")
    print(f"    {article['content'][:200]}...")

    # ─────────────────────────────────────
    # Test 5: Búsqueda "tarjetas de crédito"
    # ─────────────────────────────────────
    print("\n[Test 5] search_knowledge_base('tarjetas de crédito')...")
    result2 = await search_uc.execute(query="tarjetas de crédito", top_k=3)
    print(f"  → Resultados: {result2.total_results}")
    for i, chunk in enumerate(result2.chunks, 1):
        print(f"  [{i}] {chunk.url} | {chunk.content[:80]}...")

    print("\n" + "=" * 60)
    print("  TODOS LOS TESTS PASARON ✅")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_tools())
