from urllib.parse import urlparse
from robotexclusionrulesparser import RobotExclusionRulesParser
import httpx
from src.configuracion.ajustes import ajustes


class LectorRobots:
    """Clase que descarga y evalúa si una URL está bloqueada por el robots.txt."""

    def __init__(self, agente_usuario: str = ajustes.agente_usuario):
        self._analizador = RobotExclusionRulesParser()
        self.agente_usuario = agente_usuario
        self.dominios_analizados = set()

    async def obtener_y_analizar(self, url_base: str):
        url_analizada = urlparse(url_base)
        dominio = f"{url_analizada.scheme}://{url_analizada.netloc}"
        
        if dominio in self.dominios_analizados:
            return
            
        url_robots = f"{dominio}/robots.txt"
        
        try:
            async with httpx.AsyncClient(headers={"User-Agent": self.agente_usuario}) as cliente:
                respuesta = await cliente.get(url_robots, timeout=10.0)
                if respuesta.status_code == 200:
                    self._analizador.parse(respuesta.text)
                self.dominios_analizados.add(dominio)
        except Exception as e:
            # Si el archivo robots.txt falla, permitiremos el acceso y dejamos un log.
            print(f"[Advertencia LectorRobots] No se pudo obtener robots.txt para {dominio}: {e}")

    def esta_permitido(self, url: str) -> bool:
        """Verifica si la URL especificada tiene acceso público según el robots.txt."""
        return self._analizador.is_allowed(self.agente_usuario, url)
