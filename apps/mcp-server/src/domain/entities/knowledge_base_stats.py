from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class KnowledgeBaseStats(BaseModel):
    """Estadísticas de la base de conocimiento vectorial."""
    total_documents: int = Field(description="URLs únicas indexadas")
    total_chunks: int = Field(description="Chunks totales almacenados")
    last_updated: Optional[datetime] = Field(default=None, description="Última indexación")
    embedding_model: str = Field(default="simulated", description="Modelo de embeddings")
    avg_chunk_length: float = Field(default=0.0, description="Longitud promedio de chunk en caracteres")
    available_categories: list[str] = Field(default_factory=list, description="Categorías/Temas disponibles")
