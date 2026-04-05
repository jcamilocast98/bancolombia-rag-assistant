"""
Punto de entrada del Servidor MCP RAG — Bancolombia
Implementación usando Starlette puro para el montaje MCP para evitar conflictos de respuesta.
"""
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from mcp.server.sse import SseServerTransport
from mcp.server import Server

from src.interfaces.api.health_router import router as health_router
from src.interfaces.mcp.server import mcp_server
from src.infrastructure.config.settings import settings

logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# SseServerTransport usa scope.get("root_path") para construir la URL.
# root_path será "/mcp", por lo que "/mcp" + "/messages" = "/mcp/messages".
sse_transport = SseServerTransport("/messages")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 50)
    logger.info("  MCP Server RAG — Bancolombia (Starlette Mount)")
    logger.info("=" * 50)
    yield

# APP PRINCIPAL
app = FastAPI(
    title="Bancolombia RAG MCP Server",
    version="1.0.0",
    lifespan=lifespan,
)

from starlette.requests import Request
from starlette.responses import Response

# HANDLERS ASGI PUROS PARA MCP
async def handle_sse(scope, receive, send):
    """Maneja la conexión SSE inicial como una aplicación ASGI pura."""
    logger.info(f"[MCP-ASGI] Nueva conexión SSE")
    async with sse_transport.connect_sse(scope, receive, send) as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options()
        )

# DISPATCHER ASGI PARA MCP
async def mcp_router(scope, receive, send):
    """Enruta peticiones /sse y /messages dentro del montaje /mcp."""
    path = scope.get("path", "")
    
    # Matching más robusto que ignora prefijos residuales y slashes
    if "/sse" in path:
        await handle_sse(scope, receive, send)
    elif "/messages" in path:
        await sse_transport.handle_post_message(scope, receive, send)
    else:
        # 404 para otras rutas dentro de /mcp
        logger.warning(f"[MCP-ASGI] Ruta no encontrada en montaje /mcp: {path}")
        response = Response("Not Found", status_code=404)
        await response(scope, receive, send)

# Montar el dispatcher en el nivel superior de /mcp
app.mount("/mcp", mcp_router)

# Health router (en app principal)
app.include_router(health_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.mcp_server_port)
