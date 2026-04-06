import asyncio
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from src.configuracion.ajustes import ajustes
from src.infraestructura.persistencia.modelos import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_database():
    """Inicializa la base de datos: crea extensión pgvector y tablas."""
    logger.info(f"Conectando a {ajustes.url_base_datos} para inicialización...")
    
    engine = create_async_engine(ajustes.url_base_datos)
    
    try:
        async with engine.begin() as conn:
            # 1. Asegurar extensión pgvector
            logger.info("Asegurando extensión 'vector'...")
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            
            # 2. Crear tablas definidas en los modelos
            logger.info("Creando tablas vinculadas al Base de SQLAlchemy...")
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("¡Base de datos inicializada exitosamente!")
    except Exception as e:
        logger.error(f"Error inicializando base de datos: {e}")
        raise e
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_database())
