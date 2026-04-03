import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..infrastructure.config.settings import settings
from ..infrastructure.persistence.database import engine, Base
from .api.v1.chat_router import router as chat_router
from .api.v1.health_router import router as health_router
from .middleware.error_handler import setup_exception_handlers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup DB
    async with engine.begin() as conn:
        # Create tables locally (In prod should use alembic)
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database asíncrona iniciada y tablas verificadas.")
    yield
    # Cleanup DB
    await engine.dispose()
    logger.info("Conexiones a base de datos cerradas.")

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(chat_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")

# Handlers globales
setup_exception_handlers(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.interfaces.main:app", host="0.0.0.0", port=8000, reload=True)
