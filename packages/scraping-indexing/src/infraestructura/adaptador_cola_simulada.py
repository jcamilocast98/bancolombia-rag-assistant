from typing import Optional
from collections import deque
from src.dominio.entidades.crawl_job import CrawlJob
from src.dominio.puertos.puerto_cola import PuertoCola


class AdaptadorColaSimulada(PuertoCola):
    """Adaptador de cola simulada que utiliza una lista doblemente enlazada (deque) en memoria."""

    def __init__(self):
        self._cola = deque()
        self._visitadas = set()

    def encolar(self, trabajo: CrawlJob) -> bool:
        if not self.ha_sido_visitada(trabajo.url):
            self._cola.append(trabajo)
            return True
        return False

    def desencolar(self) -> Optional[CrawlJob]:
        if self._cola:
            return self._cola.popleft()
        return None

    def ha_sido_visitada(self, url: str) -> bool:
        return url in self._visitadas

    def marcar_como_visitada(self, url: str) -> None:
        self._visitadas.add(url)
