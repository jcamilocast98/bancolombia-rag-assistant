from abc import ABC, abstractmethod
from typing import Optional

from src.dominio.entidades.crawl_job import CrawlJob


class PuertoCola(ABC):
    """Puerto (interfaz) abstracto para gestionar la cola de URLs."""

    @abstractmethod
    def encolar(self, trabajo: CrawlJob) -> bool:
        """Encola un nuevo trabajo de rastreo."""
        pass

    @abstractmethod
    def desencolar(self) -> Optional[CrawlJob]:
        """Extrae el siguiente trabajo de rastreo de la cola."""
        pass

    @abstractmethod
    def ha_sido_visitada(self, url: str) -> bool:
        """Verifica si la URL ya ha sido encolada o visitada."""
        pass

    @abstractmethod
    def marcar_como_visitada(self, url: str) -> None:
        """Marca una URL como visitada para prevenir su re-rastreo."""
        pass
