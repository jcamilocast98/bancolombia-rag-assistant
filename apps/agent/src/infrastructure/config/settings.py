from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Bancolombia AI Agent"
    version: str = "1.0.0"
    api_key: str = "test-api-key"
    
    anthropic_api_key: str | None = None
    gemini_api_key: str | None = None
    mcp_server_command: str = "python"
    mcp_server_args: str = "-m;scraping_indexing.server"
    mcp_transport: str = "stdio" # stdio o sse
    mcp_sse_url: str = ""
    
    database_url: str = "sqlite+aiosqlite:///./agent.db"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
