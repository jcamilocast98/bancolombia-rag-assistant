from fastapi import Request, status
from fastapi.responses import JSONResponse
from ...domain.exceptions.domain_exceptions import DomainException
from ...domain.exceptions.llm_exceptions import LLMTimeoutError
from ...domain.exceptions.mcp_exceptions import MCPConnectionError
import logging

logger = logging.getLogger(__name__)

async def domain_exception_handler(request: Request, exc: DomainException):
    logger.error(f"Domain error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc), "error_type": exc.__class__.__name__}
    )

async def llm_timeout_handler(request: Request, exc: LLMTimeoutError):
    logger.error("LLM Timeout detectado")
    return JSONResponse(
        status_code=status.HTTP_408_REQUEST_TIMEOUT,
        content={"detail": "El servicio LLM está tardando demasiado en responder. Intenta de nuevo."}
    )

async def mcp_connection_handler(request: Request, exc: MCPConnectionError):
    logger.error("Falla de conexión MCP")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "El servicio de Base de Conocimiento no está disponible."}
    )

def setup_exception_handlers(app):
    app.add_exception_handler(DomainException, domain_exception_handler)
    app.add_exception_handler(LLMTimeoutError, llm_timeout_handler)
    app.add_exception_handler(MCPConnectionError, mcp_connection_handler)
