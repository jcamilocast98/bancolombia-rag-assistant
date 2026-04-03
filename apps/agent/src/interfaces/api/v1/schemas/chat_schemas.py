from pydantic import BaseModel
from typing import List, Optional

class ChatRequestSchema(BaseModel):
    session_id: str
    message: str

class ChatResponseSchema(BaseModel):
    reply: str
    sources: List[str] = []
