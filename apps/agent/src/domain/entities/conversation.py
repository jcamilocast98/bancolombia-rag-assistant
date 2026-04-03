from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone

from .message import Message
from ..value_objects.conversation_id import ConversationId

class Conversation(BaseModel):
    """
    Entidad que representa la sesión de conversación completa.
    """
    id: ConversationId
    messages: List[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    def add_message(self, message: Message):
        self.messages.append(message)
        self.updated_at = datetime.now(timezone.utc)
        
    def get_context_window(self, max_messages: int = 10) -> List[Message]:
        """Recupera los últimos N mensajes para contexto corto."""
        return self.messages[-max_messages:]
