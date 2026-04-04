class VectorDBConnectionError(Exception):
    """Error de conexión a la base de datos vectorial."""
    pass


class QueryError(Exception):
    """Error al ejecutar una consulta contra la base de datos."""
    pass
