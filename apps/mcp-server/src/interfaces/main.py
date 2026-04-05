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

# HANDLERS ASGI PUROS PARA MCP
async def handle_sse(scope, receive, send):
    """Maneja la conexión SSE inicial."""
    logger.info(f"[MCP] Nueva conexión SSE")
    async with sse_transport.connect_sse(scope, receive, send) as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options()
        )

async def handle_messages(scope, receive, send):
    """Maneja el envío de mensajes JSON-RPC."""
    logger.info(f"[MCP] Nuevo mensaje recibido")
    await sse_transport.handle_post_message(scope, receive, send)

# RUTAS MCP USANDO STARLETTE
mcp_routes = [
    Route("/sse", endpoint=handle_sse, methods=["GET"]),
    Route("/messages", endpoint=handle_messages, methods=["POST"]),
]
mcp_asgi_app = Starlette(routes=mcp_routes)

# Montar sub-app en /mcp
app.mount("/mcp", mcp_asgi_app)

# Health router (en app principal)
app.include_router(health_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.mcp_server_port)
