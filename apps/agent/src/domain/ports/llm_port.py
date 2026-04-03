from typing import List
from abc import ABC, abstractmethod
from ..entities.message import Message
from ..value_objects.llm_response import LLMResponse

class LLMPort(ABC):
    """
    Puerto de comunicación con el Large Language Model.
    Define las capacidades esperadas, agnósticas a si usamos OpenAI, Anthropic, etc.
    """
    @abstractmethod
    async def generate_response(self, system_prompt: str, messages: List[Message]) -> LLMResponse:
        """
        Genera una respuesta utilizando el LLM basado en el contexto provisto.
        """
        pass
