from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración del MCP Server."""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Base de datos
    database_url: str = "postgresql://raguser:changeme@localhost:5432/bancolombia_rag"

    # Gemini (embeddings + LLM)
    gemini_api_key: str = ""
    embedding_model: str = "gemini-embedding-001"

    # MCP
    mcp_transport: str = "stdio"
    mcp_server_port: int = 8001

    # App
    log_level: str = "INFO"


settings = Settings()
