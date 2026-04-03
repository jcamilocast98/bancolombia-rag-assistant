from .domain_exceptions import DomainException

class LLMBaseError(DomainException):
    """Excepción base para errores relacionados con el LLM."""
    pass

class LLMTimeoutError(LLMBaseError):
    """Lanzada cuando la petición al LLM excede el tiempo límite."""
    pass

class LLMRateLimitError(LLMBaseError):
    """Lanzada cuando se supera la cuota de peticiones al LLM."""
    pass

class LLMProviderError(LLMBaseError):
    """Lanzada cuando el proveedor del LLM devuelve un error no controlado."""
    pass
