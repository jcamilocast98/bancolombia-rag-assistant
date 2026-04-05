import logging
from typing import List
from google import genai
from src.dominio.puertos.puerto_embeddings import PuertoEmbeddings
from src.configuracion.ajustes import ajustes

logger = logging.getLogger(__name__)


class AdaptadorEmbeddingsGemini(PuertoEmbeddings):
    """
    Adaptador de embeddings utilizando Google Gemini.
    Modelo: text-embedding-004 (768 dimensiones).
    """

    def __init__(self):
        if not ajustes.clave_api_gemini:
            raise ValueError("CLAVE_API_GEMINI no configurada. Revisa tu archivo .env")
        self.client = genai.Client(api_key=ajustes.clave_api_gemini)
        self.modelo = ajustes.modelo_embedding_gemini
        self.tamano_lote = ajustes.tamano_lote_embedding

    async def generar_embeddings(self, textos: List[str]) -> List[List[float]]:
        """Genera embeddings en lotes usando Gemini text-embedding-004."""
        todos_los_embeddings: List[List[float]] = []

        for i in range(0, len(textos), self.tamano_lote):
            lote = textos[i : i + self.tamano_lote]
            logger.info(
                f"[Gemini] Generando embeddings lote {i // self.tamano_lote + 1} "
                f"({len(lote)} textos)..."
            )

            try:
                from google.genai import types
                result = self.client.models.embed_content(
                    model=self.modelo,
                    contents=lote,
                    config=types.EmbedContentConfig(output_dimensionality=768),
                )
                embeddings_lote = [emb.values for emb in result.embeddings]
                todos_los_embeddings.extend(embeddings_lote)
            except Exception as e:
                logger.error(f"[Gemini] Error generando embeddings: {e}")
                raise e

        logger.info(
            f"[Gemini] Total de embeddings generados: {len(todos_los_embeddings)} "
            f"({len(todos_los_embeddings[0]) if todos_los_embeddings else 0} dims)"
        )
        return todos_los_embeddings
