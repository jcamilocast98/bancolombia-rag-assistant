import logging
from src.domain.ports.vector_db_port import VectorDBPort
from src.domain.entities.knowledge_base_stats import KnowledgeBaseStats

logger = logging.getLogger(__name__)


class GetKnowledgeBaseStats:
    """Caso de uso: obtener estadísticas de la base de conocimiento."""

    def __init__(self, vector_db: VectorDBPort):
        self.vector_db = vector_db

    async def execute(self) -> KnowledgeBaseStats:
        stats = await self.vector_db.get_stats()
        logger.info(f"[KB Stats] {stats.total_chunks} chunks, {stats.total_documents} docs")
        return stats
