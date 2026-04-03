from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

class Pagina(BaseModel):
    """Entidad que representa una página web extraída mediante scraping."""
    url: HttpUrl
    titulo: str = Field(default="")
    contenido_html: str
    fecha_extraccion: datetime = Field(default_factory=datetime.utcnow)
    codigo_estado: int = Field(default=200)
    categoria: Optional[str] = Field(default=None)

    def es_valida(self) -> bool:
        """Verifica si la página se descargó correctamente y tiene contenido."""
        return self.codigo_estado == 200 and len(self.contenido_html) > 0
