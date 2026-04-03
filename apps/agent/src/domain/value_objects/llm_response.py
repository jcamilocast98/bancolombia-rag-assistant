from pydantic import BaseModel, Field
from typing import Optional, List
from ..entities.tool_call import ToolCall

class LLMResponse(BaseModel):
    """
    Value Object devuelto por el adaptador del LLM.
    Contiene el texto de respuesta y, si los hay, validaciones
    de tools por invocar.
    """
    content: str = ""
    tool_calls: Optional[List[ToolCall]] = Field(default_factory=list)
    sources: Optional[List[str]] = Field(default_factory=list)
    
    def requires_action(self) -> bool:
        return bool(self.tool_calls and len(self.tool_calls) > 0)
