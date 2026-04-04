from pydantic import BaseModel, Field
from typing import List
from .document_chunk import DocumentChunk


class SearchResult(BaseModel):
    """Resultado de una búsqueda en la base de conocimiento."""
    query: str
    chunks: List[DocumentChunk] = Field(default_factory=list)
    total_results: int = 0
    search_method: str = Field(default="text", description="Método: 'vector' o 'text'")
