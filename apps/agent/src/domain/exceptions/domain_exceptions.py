class DomainException(Exception):
    """Excepción base para el dominio del agente."""
    pass

class ConversationNotFoundError(DomainException):
    """Lanzada cuando una conversación solicitada no existe."""
    def __init__(self, conversation_id: str):
        super().__init__(f"No se encontró la conversación con ID: {conversation_id}")
