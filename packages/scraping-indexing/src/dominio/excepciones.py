class ErrorScrapingIndexacion(Exception):
    """Excepción base para el módulo de scraping e indexación."""
    pass

class ErrorScraping(ErrorScrapingIndexacion):
    """Excepción base para errores relacionados con el scraping."""
    pass

class ErrorRestriccionRobots(ErrorScraping):
    """Se lanza cuando el rastreo de una URL está bloqueado por robots.txt."""
    pass

class ErrorLimiteTasa(ErrorScraping):
    """Se lanza cuando se excede el límite de peticiones (rate limit)."""
    pass

class ErrorExtraccionContenido(ErrorScrapingIndexacion):
    """Excepción base para errores durante la extracción de contenido."""
    pass

class ErrorProcesamientoHTML(ErrorExtraccionContenido):
    """Se lanza cuando falla el análisis del documento HTML."""
    pass

class ErrorIndexacion(ErrorScrapingIndexacion):
    """Excepción base para errores de indexación."""
    pass

class ErrorEmbedding(ErrorIndexacion):
    """Excepción base para fallos al generar embeddings."""
    pass

class ErrorLimiteTasaEmbedding(ErrorEmbedding):
    """Se lanza cuando el proveedor de embeddings excede el límite de tasa."""
    pass

class ErrorBdVectorial(ErrorIndexacion):
    """Excepción base para las operaciones en la base de datos vectorial."""
    pass

class ErrorChunkDuplicado(ErrorBdVectorial):
    """Se lanza al intentar insertar un chunk que ya existe."""
    pass
