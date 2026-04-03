from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Ajustes(BaseSettings):
    """Configuración principal de todo el sistema."""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Configuración de Rastreo (Scraping)
    url_base: str = Field("https://www.bancolombia.com/personas", description="URL inicial por donde empezar a rastrear")
    agente_usuario: str = Field("BancolombiaRAGBot/1.0", description="User-Agent para las peticiones HTTP")
    retraso_rastreo: float = Field(2.0, description="Retraso entre cada solicitud en segundos (rate limit)")
    paginas_maximas: int = Field(50, description="Número máximo de páginas que se pueden rastrear")
    
    # Configuración de los Chunks
    tamano_chunk: int = Field(512, description="Tamaño máximo de cada fragmento textual")
    solapamiento_chunk: int = Field(64, description="Margen de solape (overlap) entre chunks consecutivos")

    # Proveedor de Embeddings (OpenAI)
    clave_api_openai: str = Field("llave-falsa", description="Clave de la API de OpenAI")
    modelo_embedding: str = Field("text-embedding-3-small", description="Modelo usado para las incrustaciones (embeddings)")
    tamano_lote_embedding: int = Field(100, description="Cantidad de chunks a procesar por cada llamada a la API")

    # Almacenamiento crudo (MinIO/S3)
    endpoint_s3: str = Field("localhost:9000")
    clave_acceso_s3: str = Field("minioadmin")
    clave_secreta_s3: str = Field("minioadmin")
    bucket_s3: str = Field("bancolombia-raw-html")

    # Gestor de Cola (Redis)
    url_redis: str = Field("redis://localhost:6379/0")

    # Base de datos Vectorial (pgvector)
    url_base_datos: str = Field("postgresql+asyncpg://usuario:clave@localhost:5432/bdvectorial")

ajustes = Ajustes()
