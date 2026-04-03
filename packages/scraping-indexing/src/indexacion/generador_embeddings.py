from typing import List
import asyncio

from src.dominio.entidades.chunk import Chunk
from src.dominio.puertos.puerto_embeddings import PuertoEmbeddings
from src.configuracion.ajustes import ajustes

class GeneradorEmbeddings:
    """Gestiona la creación de representaciones vectoriales por lotes."""
    
    def __init__(self, puerto_embeddings: PuertoEmbeddings):
        self.puerto_embeddings = puerto_embeddings
        self.tamano_lote = ajustes.tamano_lote_embedding

    async def incrustar_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        """Asigna los vectores a los objetos Chunk de entrada."""
        for i in range(0, len(chunks), self.tamano_lote):
            lote = chunks[i: i + self.tamano_lote]
            textos = [c.contenido_texto for c in lote]
            
            try:
                vectores = await self.puerto_embeddings.generar_embeddings(textos)
                for chunk, vector in zip(lote, vectores):
                    chunk.embedding = vector
            except Exception as e:
                print(f"[Error de Embedding] Fallo en el lote iniciando en índice {i}: {e}")
                # Aquí se podría implementar reintentos exponenciales
                
            # Rate limiting / retraso breve
            await asyncio.sleep(0.5)
            
        return chunks
