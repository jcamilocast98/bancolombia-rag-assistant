from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ....infrastructure.persistence.database import get_db_session

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
async def health_check(session: AsyncSession = Depends(get_db_session)):
    db_status = "ok"
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"
        
    return {
        "status": "ok",
        "database": db_status,
        "mcp_adapter": "initialized" # Could ping MCP if needed
    }
