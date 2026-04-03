from ...domain.ports.memory_port import MemoryPort
from ...domain.entities.conversation import Conversation
from ...domain.entities.message import Message
from ...domain.value_objects.conversation_id import ConversationId

class ContextualMemoryManager:
    """
    Gestiona el almacenamiento y la recuperación del historial conversacional
    (memoria de mediano plazo en DB y corto plazo inyectada en prompt).
    """
    def __init__(self, memory_port: MemoryPort):
        self.memory_port = memory_port

    async def get_or_create_conversation(self, session_id: str) -> Conversation:
        """
        Busca la conversación por su ID o crea una nueva si no existe.
        """
        conversation = await self.memory_port.get_conversation(session_id)
        if not conversation:
            conversation = Conversation(id=ConversationId(session_id))
            await self.memory_port.save_conversation(conversation)
        return conversation

    async def add_message(self, session_id: str, message: Message):
        """
        Añade un mensaje a la historia y lo persiste.
        """
        await self.memory_port.add_message_to_conversation(session_id, message)
