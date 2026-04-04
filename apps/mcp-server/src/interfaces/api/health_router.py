from fastapi import APIRouter
from src.infrastructure.adapters.pgvector_adapter import PgVectorAdapter

router = APIRouter()
_vector_db = PgVectorAdapter()


@router.get("/health")
async def health_check():
    """Health check que verifica la conexión a PostgreSQL."""
    db_ok = await _vector_db.health_check()
    status = "healthy" if db_ok else "degraded"

    return {
        "status": status,
        "service": "mcp-server",
        "dependencies": {
            "postgresql": "connected" if db_ok else "disconnected",
        },
    }
