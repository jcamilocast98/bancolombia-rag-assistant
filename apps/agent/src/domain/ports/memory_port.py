from typing import Optional
from abc import ABC, abstractmethod
from ..entities.conversation import Conversation
from ..entities.message import Message

class MemoryPort(ABC):
    """
    Puerto de persistencia para la memoria conversacional a mediano/largo plazo.
    """
    @abstractmethod
    async def save_conversation(self, conversation: Conversation) -> None:
        """Guarda o actualiza una conversación (y sus mensajes)."""
        pass

    @abstractmethod
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Obtiene una conversación por su ID, retornando None si no existe."""
        pass
        
    @abstractmethod
    async def add_message_to_conversation(self, conversation_id: str, message: Message) -> None:
        """Agrega un mensaje individual a una conversación de forma eficiente."""
        pass
