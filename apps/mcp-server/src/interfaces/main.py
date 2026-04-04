"""
Punto de entrada del Servidor MCP RAG — Bancolombia
Implementación definitiva de SSE nativo (connect_sse).
"""
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from mcp.server.sse import SseServerTransport

from src.interfaces.api.health_router import router as health_router
from src.interfaces.mcp.server import mcp_server
from src.infrastructure.config.settings import settings

logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# Definimos el transporte SSE indicando la ruta relativa /sse/messages
# para que el cliente la resuelva correctamente.
sse_transport = SseServerTransport("/sse/messages")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 50)
    logger.info("  MCP Server RAG — Bancolombia (Native SSE Corrected 2)")
    logger.info("=" * 50)
    yield
    logger.info("MCP Server cerrando...")

app = FastAPI(
    title="Bancolombia RAG MCP Server",
    version="1.0.0",
    lifespan=lifespan,
)

# Endpoint para la conexión inicial de SSE (ASGI Crudo)
async def sse_asgi(scope, receive, send):
    if scope["type"] != "http":
        return
    # sse_transport.connect_sse toma el control de la conexión ASGI
    async with sse_transport.connect_sse(scope, receive, send) as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options()
        )

# Endpoint para recibir mensajes POST (ASGI Crudo)
async def messages_asgi(scope, receive, send):
    if scope["type"] != "http":
        return
    await sse_transport.handle_post_message(scope, receive, send)

from starlette.routing import Mount

# Montamos las rutas ASGI explícitamente.
# El mount más específico debe ir primero.
app.routes.append(Mount("/sse/messages", app=messages_asgi))
app.routes.append(Mount("/sse", app=sse_asgi))

# Health router
app.include_router(health_router, prefix="/api")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error no manejado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.mcp_server_port)
