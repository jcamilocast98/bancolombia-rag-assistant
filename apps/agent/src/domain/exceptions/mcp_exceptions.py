from .domain_exceptions import DomainException

class MCPBaseError(DomainException):
    """Excepción base para errores relacionados con el servidor/protocolo MCP."""
    pass

class MCPConnectionError(MCPBaseError):
    """Lanzada cuando no se puede conectar al servidor MCP."""
    pass

class MCPToolNotFoundError(MCPBaseError):
    """Lanzada cuando el servidor MCP no dispone de la herramienta solicitada."""
    pass

class MCPExecutionError(MCPBaseError):
    """Lanzada cuando una herramienta del MCP falla en su ejecución."""
    pass
