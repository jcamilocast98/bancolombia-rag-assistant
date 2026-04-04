"""
╔══════════════════════════════════════════════════════════════╗
║   Pipeline Unificado: Scraping + Indexación                 ║
║   Bancolombia RAG — Infraestructura Real                    ║
╚══════════════════════════════════════════════════════════════╝

Conecta TODOS los servicios reales:
  - Cola de URLs:       Redis (rag-redis)
  - Almacenamiento:     MinIO S3 (rag-minio)
  - Base Vectorial:     PostgreSQL + pgvector (rag-postgres)
  - Embeddings:         OpenAI text-embedding-3-small (o simulado)

Uso:
  python -m src.pipeline
"""
import asyncio
import logging
import sys

from src.configuracion.ajustes import ajustes

# ── Adaptadores Reales de Infraestructura ──
from src.infraestructura.adaptador_cola_redis import AdaptadorColaRedis
from src.infraestructura.adaptador_almacenamiento_s3 import AdaptadorAlmacenamientoS3
from src.infraestructura.adaptador_pgvector import AdaptadorPgVector
from src.infraestructura.adaptador_embeddings_simulado import AdaptadorEmbeddingsSimulado
# Descomentar cuando se tenga una OPENAI_API_KEY válida:
# from src.infraestructura.adaptador_embeddings_openai import AdaptadorEmbeddingsOpenAI

# ── Componentes de Scraping ──
from src.scraping.lector_robots import LectorRobots
from src.scraping.rastreador import Rastreador
from src.scraping.gestor_almacenamiento import GestorAlmacenamiento

# ── Componentes de Indexación ──
from src.indexacion.limpiador_datos import LimpiadorDatos
from src.indexacion.segmentador_texto import SegmentadorTexto
from src.indexacion.generador_embeddings import GeneradorEmbeddings
from src.indexacion.acceso_bd_vectorial import AccesoBdVectorial
from src.indexacion.orquestador import OrquestadorIndexacion

# ── Persistencia BD ──
from src.infraestructura.persistencia.init_pgvector import inicializar_bd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("pipeline")


async def ejecutar_pipeline():
    """
    Ejecuta la tubería completa de Scraping → Almacenamiento → Indexación → pgvector.
    """
    logger.info("=" * 60)
    logger.info("  PIPELINE UNIFICADO — Bancolombia RAG")
    logger.info("=" * 60)

    # ╔═══════════════════════════════════════╗
    # ║ FASE 0: Inicializar Base de Datos     ║
    # ╚═══════════════════════════════════════╝
    logger.info("[Fase 0] Inicializando base de datos vectorial (pgvector)...")
    await inicializar_bd()

    # ╔═══════════════════════════════════════╗
    # ║ FASE 1: Instanciar Adaptadores        ║
    # ╚═══════════════════════════════════════╝
    logger.info("[Fase 1] Instanciando adaptadores de infraestructura...")

    cola = AdaptadorColaRedis()
    almacenamiento = AdaptadorAlmacenamientoS3()
    bd_vectorial = AdaptadorPgVector()

    # Seleccionar proveedor de embeddings según configuración
    if ajustes.proveedor_embeddings == "gemini" and ajustes.clave_api_gemini:
        from src.infraestructura.adaptador_embeddings_gemini import AdaptadorEmbeddingsGemini
        embeddings = AdaptadorEmbeddingsGemini()
        logger.info("  → Embeddings: Gemini (Reales)")
    elif ajustes.proveedor_embeddings == "openai" and ajustes.clave_api_openai and ajustes.clave_api_openai != "llave-falsa":
        from src.infraestructura.adaptador_embeddings_openai import AdaptadorEmbeddingsOpenAI
        embeddings = AdaptadorEmbeddingsOpenAI()
        logger.info("  → Embeddings: OpenAI (Reales)")
    else:
        embeddings = AdaptadorEmbeddingsSimulado()
        logger.info("  → Embeddings: Simulados (configurar CLAVE_API_GEMINI o CLAVE_API_OPENAI para reales)")

    logger.info("  → Cola:            Redis (rag-redis)")
    logger.info("  → Almacenamiento:  MinIO S3 (rag-minio)")
    logger.info("  → Base Vectorial:  PostgreSQL + pgvector (rag-postgres)")

    # ╔═══════════════════════════════════════╗
    # ║ FASE 2: Componentes de Scraping       ║
    # ╚═══════════════════════════════════════╝
    logger.info("[Fase 2] Inicializando componentes de scraping...")

    lector_robots = LectorRobots()
    rastreador = Rastreador(puerto_cola=cola, lector_robots=lector_robots)
    gestor_almacenamiento = GestorAlmacenamiento(puerto_almacenamiento=almacenamiento)

    # ╔═══════════════════════════════════════╗
    # ║ FASE 3: Componentes de Indexación     ║
    # ╚═══════════════════════════════════════╝
    logger.info("[Fase 3] Inicializando componentes de indexación...")

    limpiador = LimpiadorDatos()
    segmentador = SegmentadorTexto()
    gen_embeddings = GeneradorEmbeddings(puerto_embeddings=embeddings)
    acc_bd = AccesoBdVectorial(puerto_bd=bd_vectorial)
    orquestador = OrquestadorIndexacion(
        puerto_almacenamiento=almacenamiento,
        limpiador=limpiador,
        segmentador=segmentador,
        generador_embeddings=gen_embeddings,
        acceso_bd=acc_bd,
    )

    # ╔═══════════════════════════════════════╗
    # ║ FASE 4: SCRAPING (Rastreo Web)        ║
    # ╚═══════════════════════════════════════╝
    logger.info("[Fase 4] Comenzando rastreo web...")
    logger.info(f"  → URL Base: {ajustes.url_base}")
    logger.info(f"  → Máx. Páginas: {ajustes.paginas_maximas}")
    logger.info(f"  → Profundidad: {ajustes.profundidad_maxima}")

    await rastreador.iniciar_base()

    rutas_almacenadas = []  # Guardaremos las llaves S3 para indexar después

    continuar = True
    while continuar:

        async def descargar_guardar_y_registrar(url: str):
            """Descarga la página, la guarda en MinIO y registra la ruta."""
            ruta = await gestor_almacenamiento.procesar_y_guardar(url)
            rutas_almacenadas.append((ruta, url))
            logger.info(f"  [S3] Guardado: {url} → {ruta}")
            # Retornar la Pagina para que el rastreador extraiga enlaces
            return await gestor_almacenamiento.extractor.descargar_pagina(url)

        continuar = await rastreador.procesar_trabajo(
            funcion_extraccion=descargar_guardar_y_registrar
        )

    logger.info(f"[Fase 4] Scraping completado. {len(rutas_almacenadas)} páginas almacenadas en MinIO.")

    # ╔═══════════════════════════════════════╗
    # ║ FASE 5: INDEXACIÓN (Vectorización)    ║
    # ╚═══════════════════════════════════════╝
    logger.info("[Fase 5] Comenzando indexación vectorial...")

    exitosos = 0
    fallidos = 0

    for ruta, url in rutas_almacenadas:
        try:
            metadatos = {"url_origen": url, "fuente": "bancolombia.com"}
            resultado = await orquestador.procesar_documento(
                ruta_almacenamiento=ruta,
                url_origen=url,
                metadatos=metadatos,
            )
            if resultado:
                exitosos += 1
            else:
                fallidos += 1
        except Exception as e:
            logger.error(f"  [ERROR] Fallo indexando {url}: {e}")
            fallidos += 1

    # ╔═══════════════════════════════════════╗
    # ║ RESUMEN FINAL                         ║
    # ╚═══════════════════════════════════════╝
    logger.info("=" * 60)
    logger.info("  RESUMEN DEL PIPELINE")
    logger.info("=" * 60)
    logger.info(f"  Páginas rastreadas:      {len(rutas_almacenadas)}")
    logger.info(f"  Indexaciones exitosas:   {exitosos}")
    logger.info(f"  Indexaciones fallidas:   {fallidos}")
    logger.info(f"  Almacenamiento:          MinIO (bucket: {ajustes.bucket_s3})")
    logger.info(f"  Base Vectorial:          pgvector (tabla: chunks)")
    logger.info("=" * 60)
    logger.info("  PIPELINE FINALIZADO EXITOSAMENTE")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(ejecutar_pipeline())
