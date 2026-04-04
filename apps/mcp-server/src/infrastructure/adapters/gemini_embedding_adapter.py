import logging
from typing import List
from google import genai
from src.domain.ports.embedding_port import EmbeddingPort
from src.domain.exceptions.embedding_exceptions import EmbeddingGenerationError
from src.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)


class GeminiEmbeddingAdapter(EmbeddingPort):
    """
    Adaptador de embeddings usando Gemini (text-embedding-004).
    Genera vectores de 768 dimensiones (nativo de Gemini).
    """

    def __init__(self):
        if not settings.gemini_api_key:
            logger.warning("[GeminiEmbed] Sin GEMINI_API_KEY. Embeddings no disponibles.")
            self._client = None
        else:
            self._client = genai.Client(api_key=settings.gemini_api_key)

    async def generate_query_embedding(self, text: str) -> List[float]:
        if not self._client:
            raise EmbeddingGenerationError("GEMINI_API_KEY no configurada para embeddings.")

        try:
            result = self._client.models.embed_content(
                model=settings.embedding_model,
                contents=text,
            )
            embedding = result.embeddings[0].values
            logger.info(f"[GeminiEmbed] Embedding generado ({len(embedding)} dims) para: '{text[:50]}...'")
            return embedding
        except Exception as e:
            raise EmbeddingGenerationError(f"Error generando embedding con Gemini: {e}")
