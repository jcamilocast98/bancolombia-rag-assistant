from typing import List
from src.dominio.puertos.puerto_embeddings import PuertoEmbeddings


class AdaptadorEmbeddingsSimulado(PuertoEmbeddings):
    """Adaptador de Embeddings simulado que retorna vectores falsos sin llamar a la API."""

    async def generar_embeddings(self, textos: List[str]) -> List[List[float]]:
        # openai text-embedding-3-small genera 1536 dimensiones, retornamos un vector falso:
        tamano_simulado = 1536
        return [[0.1] * tamano_simulado for _ in textos]
