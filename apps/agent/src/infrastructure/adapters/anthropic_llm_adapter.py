from typing import List, Optional
from anthropic import AsyncAnthropic
from ...domain.ports.llm_port import LLMPort
from ...domain.entities.message import Message
from ...domain.entities.tool_call import ToolCall
from ...domain.value_objects.llm_response import LLMResponse
from ...domain.exceptions.llm_exceptions import LLMProviderError, LLMTimeoutError
import logging

logger = logging.getLogger(__name__)

class AnthropicLLMAdapter(LLMPort):
    def __init__(self, api_key: str, available_tools_schema: Optional[List[dict]] = None):
        if not api_key or api_key == "test-api-key":
             logger.warning("No se proporcionó API key válida para Anthropic, el LLM fallará si se invoca.")
        self.client = AsyncAnthropic(
            api_key=api_key,
            default_headers={"anthropic-version": "2023-06-01"}
        )
        self.available_tools_schema = available_tools_schema or []

    async def generate_response(self, system_prompt: str, messages: List[Message]) -> LLMResponse:
        anthropic_messages = []
        for msg in messages:
            if msg.is_user():
                anthropic_messages.append({"role": "user", "content": msg.content})
            elif msg.is_assistant():
                # Reconstruir de manera adecuada blocks de tool_calls si las hay
                content_blocks = []
                if msg.content:
                    content_blocks.append({"type": "text", "text": msg.content})
                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        content_blocks.append({
                            "type": "tool_use",
                            "id": tc.id,
                            "name": tc.name,
                            "input": tc.arguments
                        })
                if not content_blocks:
                    content_blocks.append({"type": "text", "text": " "}) # Evitar bloque vacío
                anthropic_messages.append({"role": "assistant", "content": content_blocks})
            elif msg.is_tool():
                anthropic_messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": msg.tool_call_id,
                        "content": msg.content
                    }]
                })

        try:
            kwargs = {
                "model": "claude-3-5-haiku-20241022",
                "max_tokens": 1024,
                "system": system_prompt,
                "messages": anthropic_messages,
            }
            logger.info(f"Invocando Anthropic con modelo: {kwargs['model']}")
            if self.available_tools_schema:
                kwargs["tools"] = self.available_tools_schema

            response = await self.client.messages.create(**kwargs)
            
            tool_calls: List[ToolCall] = []
            text_response = ""
            for block in response.content:
                if block.type == "text":
                    text_response += block.text
                elif block.type == "tool_use":
                    tool_calls.append(ToolCall(
                        id=block.id,
                        name=block.name,
                        arguments=block.input
                    ))
                    
            # sources = [] logica para parsear URLs si el tool nos obligaba, pero delegamos al LLM el citarlo en el text_response.
            
            return LLMResponse(content=text_response, tool_calls=tool_calls)

        except Exception as e:
            logger.error(f"Error invocando Anthropic: {e}")
            raise LLMProviderError(f"Falla en comunicación con Claude: {e}")
