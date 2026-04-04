import redis
import json
import logging
from typing import Optional
from src.dominio.entidades.crawl_job import CrawlJob
from src.dominio.puertos.puerto_cola import PuertoCola
from src.configuracion.ajustes import ajustes

logger = logging.getLogger(__name__)

class AdaptadorColaRedis(PuertoCola):
    """
    Adaptador de cola real utilizando Redis.
    Proporciona persistencia para que el rastreo pueda reanudarse tras un reinicio.
    """

    def __init__(self):
        # Conexión a Redis usando la URL de configuración
        try:
            self.client = redis.from_url(ajustes.url_redis, decode_responses=True)
            # Ping para validar conexión
            self.client.ping()
            logger.info(f"Conectado a Redis exitosamente en {ajustes.url_redis}")
        except Exception as e:
            logger.error(f"Error conectando a Redis: {e}")
            raise e

        # Llaves con prefijo para mantener el orden y evitar colisiones
        self.PREFIJO = "bancolombia:rag:"
        self.KEY_COLA = f"{self.PREFIJO}cola"
        self.KEY_VISITADAS = f"{self.PREFIJO}visitadas"

    def encolar(self, trabajo: CrawlJob) -> bool:
        """Inserta un trabajo al inicio de la lista (LPUSH)."""
        if not self.ha_sido_visitada(trabajo.url):
            # Serializar a JSON
            datos = trabajo.model_dump_json()
            # Push a la izquierda (inicio de cola)
            self.client.lpush(self.KEY_COLA, datos)
            return True
        return False

    def desencolar(self) -> Optional[CrawlJob]:
        """Extrae un trabajo del final de la lista (RPOP)."""
        # Extraer de la derecha (final de cola - FIFO)
        datos = self.client.rpop(self.KEY_COLA)
        if not datos:
            return None
        
        try:
            # Rehidratar el objeto Pydantic
            diccionario = json.loads(datos)
            return CrawlJob(**diccionario)
        except Exception as e:
            logger.error(f"Error de deserialización en cola Redis: {e}")
            return None

    def ha_sido_visitada(self, url: str) -> bool:
        """Verifica si la URL existe en el Set de visitadas."""
        return self.client.sismember(self.KEY_VISITADAS, url) == 1

    def marcar_como_visitada(self, url: str) -> None:
        """Agrega la URL al Set de visitadas."""
        self.client.sadd(self.KEY_VISITADAS, url)
