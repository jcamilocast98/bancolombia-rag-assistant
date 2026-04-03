from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from .tool_call import ToolCall

class Message(BaseModel):
    """
    Entidad que representa un mensaje en la conversación.
    """
    role: str # 'user', 'assistant', 'system', 'tool'
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None # Utilizado si role='tool' para referenciar el ID de llamada
    
    def is_user(self) -> bool:
        return self.role == "user"
    
    def is_assistant(self) -> bool:
        return self.role == "assistant"
        
    def is_tool(self) -> bool:
        return self.role == "tool"
