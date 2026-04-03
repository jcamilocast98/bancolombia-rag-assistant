from src.scraping.rastreador import Rastreador
from src.infraestructura.adaptador_cola_simulada import AdaptadorColaSimulada
from src.scraping.lector_robots import LectorRobots

# --- Pruebas Scraping ---

def test_rastreador_extraccion_enlaces():
    cola = AdaptadorColaSimulada()
    robots = LectorRobots()
    rastreador = Rastreador(puerto_cola=cola, lector_robots=robots)
    
    # Forzamos el dominio_base para validar el filtro
    rastreador.dominio_base = "www.bancolombia.com"
    
    html = """
        <a href="/personas/cuentas">Cuentas</a>
        <a href="https://www.bancolombia.com/personas/creditos">Creditos</a>
        <a href="https://externo.com">Externo</a>
        <a href="/personas/documento.pdf">Archivo PDF</a>
    """
    
    enlaces = rastreador.extraer_enlaces(html, "https://www.bancolombia.com/personas")
    
    assert "https://www.bancolombia.com/personas/cuentas" in enlaces
    assert "https://www.bancolombia.com/personas/creditos" in enlaces
    assert "https://externo.com" not in enlaces
    assert "https://www.bancolombia.com/personas/documento.pdf" not in enlaces
