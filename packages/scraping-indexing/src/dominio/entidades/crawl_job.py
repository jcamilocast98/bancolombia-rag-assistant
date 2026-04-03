from pydantic import BaseModel, ConfigDict

class CrawlJob(BaseModel):
    """Entidad que representa un trabajo en cola para rastrear (scrape) una URL."""
    url: str
    profundidad: int = 0
    
    # Configuración para evitar conflictos de nombres ('model_')
    model_config = ConfigDict(protected_namespaces=())
