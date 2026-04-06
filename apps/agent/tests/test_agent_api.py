import pytest
from fastapi.testclient import TestClient
from src.interfaces.main import app

client = TestClient(app)

def test_health_check_endpoint():
    """
    Verifica que el endpoint de salud responda correctamente.
    Prueba de humo básica para asegurar que la app carga.
    """
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    # En el ambiente real, la DB podría no estar o fallar, pero status suele ser 'ok'
    assert response.json()["status"] == "ok"

def test_app_initialization():
    """
    Verifica que la instancia de FastAPI esté correctamente configurada.
    """
    assert "Bancolombia AI Agent" in app.title
    assert len(app.routes) > 0
