"""
Script de inicialización de la Base de Datos Vectorial.
Crea la extensión pgvector y las tablas necesarias en PostgreSQL.
"""
import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from src.infraestructura.persistencia.modelos import Base
from src.configuracion.ajustes import ajustes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def inicializar_bd():
    """Crea la extensión vector y todas las tablas del esquema."""
    engine = create_async_engine(ajustes.url_base_datos, echo=True)

    async with engine.begin() as conn:
        # 1. Habilitar la extensión pgvector
        logger.info("Habilitando extensión 'vector' en PostgreSQL...")
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

        # 2. Crear todas las tablas definidas en modelos.py
        logger.info("Creando tablas...")
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Base de datos vectorial inicializada correctamente.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(inicializar_bd())
