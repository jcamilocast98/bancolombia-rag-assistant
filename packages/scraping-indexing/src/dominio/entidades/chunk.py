from typing import Optional, List
from pydantic import BaseModel, Field

class Chunk(BaseModel):
    """Entidad que representa un chunk (segmento) de texto preparado para embeddings."""
    id_chunk: str = Field(description="Identificador único del chunk, útil para evitar duplicados")
    url: str
    contenido_texto: str
    indice_chunk: int = Field(description="Índice secuencial de este chunk dentro de la página")
    embedding: Optional[List[float]] = Field(default=None, description="Representación vectorial")
    metadatos: dict = Field(default_factory=dict, description="Información de contexto como el título, encabezados, etc.")
