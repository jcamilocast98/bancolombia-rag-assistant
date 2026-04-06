from typing import List
from src.dominio.puertos.puerto_embeddings import PuertoEmbeddings


class AdaptadorEmbeddingsSimulado(PuertoEmbeddings):
    """Adaptador de Embeddings simulado que retorna vectores falsos sin llamar a la API."""

    async def generar_embeddings(self, textos: List[str]) -> List[List[float]]:
        # text-embedding-004 de Gemini genera 768 dimensiones, los vectores falsos deben coincidir:
        tamano_simulado = 768
        return [[0.1] * tamano_simulado for _ in textos]
