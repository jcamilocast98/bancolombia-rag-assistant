from pydantic import BaseModel, ConfigDict
from typing import Any, Dict, Optional

class ToolCall(BaseModel):
    """
    Entidad que representa una invocación de herramienta por parte del LLM.
    """
    id: str
    name: str
    arguments: Dict[str, Any]
    result: Optional[str] = None
    
    model_config = ConfigDict(frozen=False)

    def set_result(self, result: str):
        self.result = result
