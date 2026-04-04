import logging
from typing import List
from openai import AsyncOpenAI
from src.dominio.puertos.puerto_embeddings import PuertoEmbeddings
from src.configuracion.ajustes import ajustes

logger = logging.getLogger(__name__)


class AdaptadorEmbeddingsOpenAI(PuertoEmbeddings):
    """
    Adaptador real de embeddings utilizando la API de OpenAI.
    Modelo: text-embedding-3-small (1536 dimensiones).
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=ajustes.clave_api_openai)
        self.modelo = ajustes.modelo_embedding
        self.tamano_lote = ajustes.tamano_lote_embedding

    async def generar_embeddings(self, textos: List[str]) -> List[List[float]]:
        """Genera embeddings en lotes para optimizar las llamadas a la API."""
        todos_los_embeddings: List[List[float]] = []

        # Procesar en lotes
        for i in range(0, len(textos), self.tamano_lote):
            lote = textos[i : i + self.tamano_lote]
            logger.info(
                f"[OpenAI] Generando embeddings para lote {i // self.tamano_lote + 1} "
                f"({len(lote)} textos)..."
            )

            try:
                respuesta = await self.client.embeddings.create(
                    input=lote,
                    model=self.modelo,
                )
                embeddings_lote = [dato.embedding for dato in respuesta.data]
                todos_los_embeddings.extend(embeddings_lote)
            except Exception as e:
                logger.error(f"[OpenAI] Error generando embeddings: {e}")
                raise e

        logger.info(
            f"[OpenAI] Total de embeddings generados: {len(todos_los_embeddings)}"
        )
        return todos_los_embeddings
