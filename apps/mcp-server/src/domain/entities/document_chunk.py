from pydantic import BaseModel, Field
from typing import Optional, List


class DocumentChunk(BaseModel):
    """Fragmento de documento recuperado de la base de conocimiento."""
    chunk_id: str
    url: str
    content: str
    score: float = Field(default=0.0, description="Similitud coseno (0-1)")
    metadata: dict = Field(default_factory=dict)
