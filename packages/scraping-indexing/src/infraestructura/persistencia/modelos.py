from sqlalchemy import Column, String, Integer, Text, JSON, DateTime, func
from sqlalchemy.orm import declarative_base
from sqlalchemy.types import UserDefinedType

Base = declarative_base()


class VectorType(UserDefinedType):
    """Tipo personalizado de SQLAlchemy para la columna 'vector' de pgvector.
    Evita depender de la librería pgvector de Python (que requiere numpy).
    """
    cache_ok = True

    def __init__(self, dim: int = 768):
        self.dim = dim

    def get_col_spec(self):
        return f"vector({self.dim})"

    def bind_expression(self, bindvalue):
        return bindvalue

    def bind_processor(self, dialect):
        def process(value):
            if value is None:
                return None
            # Convertir lista de floats a formato pgvector: '[0.1, 0.2, ...]'
            return f"[{','.join(str(v) for v in value)}]"
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            if value is None:
                return None
            # Convertir string pgvector de vuelta a lista de floats
            return [float(v) for v in value.strip('[]').split(',')]
        return process


class ChunkModel(Base):
    """
    Modelo de base de datos para almacenar fragmentos (chunks) de texto y sus vectores.
    Optimizado para búsqueda semántica con pgvector.
    """
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chunk_id = Column(String(64), unique=True, index=True, nullable=False)
    url = Column(String(512), index=True, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(VectorType(768))  # 768 dimensiones para text-embedding-004 (Gemini)
    metadata_json = Column(JSON, server_default='{}')
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<ChunkModel(chunk_id={self.chunk_id}, url={self.url})>"
