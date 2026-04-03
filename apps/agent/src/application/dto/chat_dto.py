from pydantic import BaseModel
from typing import Optional, List

class ChatRequestDTO(BaseModel):
    session_id: str
    message: str

class ChatResponseDTO(BaseModel):
    reply: str
    sources: List[str] = []
