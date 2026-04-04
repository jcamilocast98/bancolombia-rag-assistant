"""
Punto de entrada del Servidor MCP RAG — Bancolombia
FastAPI + MCP Server (stdio / SSE)
"""
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from src.interfaces.api.health_router import router as health_router
from src.infrastructure.config.settings import settings

logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 50)
    logger.info("  MCP Server RAG — Bancolombia")
    logger.info(f"  Transporte: {settings.mcp_transport}")
    logger.info(f"  Embedding model: {settings.embedding_model}")
    logger.info("=" * 50)
    yield
    logger.info("MCP Server cerrando...")


app = FastAPI(
    title="Bancolombia RAG MCP Server",
    description="Servidor MCP que expone herramientas de búsqueda semántica sobre la base de conocimiento de Bancolombia.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health_router)


# --- Modo stdio (para comunicación directa con el Agente) ---
def run_stdio():
    """Ejecuta el MCP Server en modo stdio."""
    import asyncio
    from mcp.server.stdio import stdio_server
    from src.interfaces.mcp.server import mcp_server

    async def _run():
        async with stdio_server() as (read_stream, write_stream):
            await mcp_server.run(read_stream, write_stream, mcp_server.create_initialization_options())

    asyncio.run(_run())


if __name__ == "__main__":
    if settings.mcp_transport == "stdio":
        run_stdio()
    else:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=settings.mcp_server_port)
