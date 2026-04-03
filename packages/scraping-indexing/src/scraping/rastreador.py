from urllib.parse import urlparse, urljoin
import asyncio
from bs4 import BeautifulSoup
from typing import Set, Callable, Awaitable

from src.dominio.puertos.puerto_cola import PuertoCola
from src.dominio.entidades.crawl_job import CrawlJob
from src.dominio.entidades.pagina import Pagina
from src.scraping.lector_robots import LectorRobots
from src.configuracion.ajustes import ajustes


class Rastreador:
    """Explora el sitio web dinámicamente para descubrir enlaces internos."""
    
    def __init__(self, puerto_cola: PuertoCola, lector_robots: LectorRobots):
        self.cola = puerto_cola
        self.lector_robots = lector_robots
        self.dominio_base = urlparse(ajustes.url_base).netloc
        self.retraso = ajustes.retraso_rastreo
        self.paginas_maximas = ajustes.paginas_maximas
        self._contador_rastreo = 0

    async def iniciar_base(self):
        """Prepara el robot.txt para la URL base y encola el primer trabajo."""
        await self.lector_robots.obtener_y_analizar(ajustes.url_base)
        self.cola.encolar(CrawlJob(url=ajustes.url_base, profundidad=0))

    def _es_enlace_interno_valido(self, url: str) -> bool:
        """Filtra enlaces externos o activos no útiles."""
        analizado = urlparse(url)
        # Comprobar dominio
        if analizado.netloc and analizado.netloc != self.dominio_base:
            return False
        # Filtrar extensiones o archivos estáticos
        extensiones_ignoradas = {'.pdf', '.jpg', '.jpeg', '.png', '.svg', '.js', '.css', '.zip'}
        if any(analizado.path.lower().endswith(ext) for ext in extensiones_ignoradas):
            return False
        return True

    def extraer_enlaces(self, contenido_html: str, url_origen: str) -> Set[str]:
        """Busca y retorna todos los enlaces internos de un HTML."""
        sopa = BeautifulSoup(contenido_html, "html.parser")
        enlaces = set()
        for etiqueta_a in sopa.find_all('a', href=True):
            href = etiqueta_a['href']
            # Normalizar URL
            url_completa = urljoin(url_origen, href)
            # Eliminar anclas lógicas locales (ej: #seccion)
            url_completa = urlparse(url_completa)._replace(fragment="").geturl()
            
            if self._es_enlace_interno_valido(url_completa):
                enlaces.add(url_completa)
        return enlaces

    async def procesar_trabajo(self, funcion_extraccion: Callable[[str], Awaitable[Pagina]]) -> bool:
        """
        Saca un trabajo de la cola y procesa sus enlaces.
        Retorna True si debe seguir, False si alcanzó el límite o está vacío.
        """
        if self._contador_rastreo >= self.paginas_maximas:
            print(f"[Rastreador] Se alcanzó el límite configurado: {self.paginas_maximas} páginas")
            return False

        trabajo = self.cola.desencolar()
        if not trabajo:
            print("[Rastreador] La cola está vacía.")
            return False

        url = trabajo.url
        self.cola.marcar_como_visitada(url)

        if not self.lector_robots.esta_permitido(url):
            print(f"[Rastreador] Bloqueado por robots.txt: {url}")
            return True

        print(f"[Rastreador] Visitando ({self._contador_rastreo+1}/{self.paginas_maximas}): {url}")
        
        try:
            # Llamamos a extraer el HTML exteriormente para separar responsabilidades
            pagina = await funcion_extraccion(url)
            
            enlaces_nuevos = self.extraer_enlaces(pagina.contenido_html, url)
            for nuevo_enlace in enlaces_nuevos:
                if not self.cola.ha_sido_visitada(nuevo_enlace):
                    self.cola.encolar(CrawlJob(url=nuevo_enlace, profundidad=trabajo.profundidad + 1))
            
            self._contador_rastreo += 1
            await asyncio.sleep(self.retraso)  # Rate limiting para evitar saturar el servidor
        except Exception as e:
            print(f"[Rastreador] Error al rastrear {url}: {e}")
        
        return True
