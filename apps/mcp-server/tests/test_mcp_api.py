import pytest
from fastapi.testclient import TestClient
from src.interfaces.main import app

client = TestClient(app)

def test_mcp_health_check_endpoint():
    """
    Verifica que el servidor MCP tenga un endpoint de salud funcional.
    """
    response = client.get("/api/health")
    assert response.status_code == 200
    # Puede ser 'healthy' o 'degraded' dependiendo de la DB en CI
    assert response.json()["service"] == "mcp-server"

def test_mcp_server_info():
    """
    Verifica los metadatos básicos del servidor.
    """
    assert "Bancolombia RAG MCP Server" in app.title
