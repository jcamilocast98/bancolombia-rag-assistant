import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from src.dominio.entidades.chunk import Chunk
from src.infraestructura.adaptador_pgvector import AdaptadorPgVector


async def test_pgvector_integration():
    print("--- Iniciando prueba de Integración con pgvector ---")

    # 1. Instanciar adaptador
    try:
        adaptador = AdaptadorPgVector()
        print(" [OK] Adaptador pgvector instanciado.")
    except Exception as e:
        print(f" [ERROR] Fallo al instanciar: {e}")
        return

    # 2. Crear chunks de prueba con embedding falso (solo para validar inserción)
    embedding_falso = [0.01 * i for i in range(1536)]

    chunks_test = [
        Chunk(
            id_chunk="test-1",
            url="https://www.bancolombia.com/personas/cuentas",
            contenido_texto="Cuentas de Ahorro Bancolombia: sin cuota de manejo y con beneficios exclusivos.",
            indice_chunk=0,
            embedding=embedding_falso,
            metadatos={"titulo": "Cuentas de Ahorro", "seccion": "Personas"},
        ),
        Chunk(
            id_chunk="test-2",
            url="https://www.bancolombia.com/personas/cuentas",
            contenido_texto="Abre tu cuenta desde la App Bancolombia en minutos, sin papeleos.",
            indice_chunk=1,
            embedding=embedding_falso,
            metadatos={"titulo": "Cuentas de Ahorro", "seccion": "Personas"},
        ),
    ]

    # 3. Insertar
    print(" Insertando 2 chunks de prueba en pgvector...")
    try:
        await adaptador.insertar_chunks(chunks_test)
        print(" [OK] Chunks insertados exitosamente en PostgreSQL.")
    except Exception as e:
        print(f" [ERROR] Fallo al insertar: {e}")
        return

    # 4. Verificar con query directo
    from sqlalchemy import text

    async with adaptador.async_session() as session:
        result = await session.execute(
            text("SELECT chunk_id, url, LEFT(content, 60) as content_preview FROM chunks")
        )
        rows = result.fetchall()
        print(f"\n [RESULTADO] {len(rows)} chunk(s) encontrados en la BD:")
        for row in rows:
            print(f"   - {row.chunk_id[:16]}... | {row.url} | {row.content_preview}")

    print("\n--- Prueba finalizada ---")


if __name__ == "__main__":
    asyncio.run(test_pgvector_integration())
