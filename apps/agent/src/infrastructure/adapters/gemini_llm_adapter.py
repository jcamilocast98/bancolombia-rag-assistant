import logging
from typing import List, Optional
from google import genai
from google.genai import types

from ...domain.ports.llm_port import LLMPort
from ...domain.entities.message import Message
from ...domain.entities.tool_call import ToolCall
from ...domain.value_objects.llm_response import LLMResponse
from ...domain.exceptions.llm_exceptions import LLMProviderError

logger = logging.getLogger(__name__)

class GeminiLLMAdapter(LLMPort):
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash-latest", available_tools_schema: Optional[List[dict]] = None):
        if not api_key or api_key == "test-api-key":
             logger.warning("No se proporcionó API key válida para Gemini. El cliente no se inicializará.")
        
        self._api_key = api_key
        self._model_name = model_name
        self._client = None
        self.available_tools_schema = available_tools_schema or []

    @property
    def client(self) -> genai.Client:
        if self._client is None:
            if not self._api_key:
                raise LLMProviderError("No se puede inicializar Gemini: falta GEMINI_API_KEY")
            self._client = genai.Client(api_key=self._api_key)
        return self._client

    def _map_type(self, json_type: str) -> types.Type:
        mapping = {
            "string": types.Type.STRING,
            "integer": types.Type.INTEGER,
            "number": types.Type.NUMBER,
            "boolean": types.Type.BOOLEAN,
            "object": types.Type.OBJECT,
            "array": types.Type.ARRAY,
        }
        return mapping.get(json_type.lower(), types.Type.STRING)

    def _map_schema(self, schema_dict: dict) -> types.Schema:
        schema = types.Schema(type=self._map_type(schema_dict.get("type", "string")))
        if "description" in schema_dict:
            schema.description = schema_dict["description"]
        if "properties" in schema_dict:
            schema.properties = {}
            for k, v in schema_dict["properties"].items():
                schema.properties[k] = self._map_schema(v)
        if "required" in schema_dict:
            schema.required = schema_dict["required"]
        return schema

    def _get_gemini_tools(self) -> List[types.Tool]:
        if not self.available_tools_schema:
            return None
        
        declarations = []
        for tool in self.available_tools_schema:
            declarations.append(
                types.FunctionDeclaration(
                    name=tool["name"],
                    description=tool.get("description", ""),
                    parameters=self._map_schema(tool.get("input_schema", {}))
                )
            )
        return [types.Tool(function_declarations=declarations)]

    def _find_tool_name(self, tool_call_id: str, messages: List[Message]) -> str:
        for m in messages:
            if m.is_assistant() and m.tool_calls:
                for tc in m.tool_calls:
                    if tc.id == tool_call_id:
                        return tc.name
        return tool_call_id

    async def generate_response(self, system_prompt: str, messages: List[Message]) -> LLMResponse:
        contents = []
        
        for msg in messages:
            if msg.is_user():
                contents.append(types.Content(role="user", parts=[types.Part.from_text(text=msg.content)]))
            elif msg.is_assistant():
                parts = []
                if msg.content:
                    parts.append(types.Part.from_text(text=msg.content))
                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        parts.append(types.Part.from_function_call(
                            name=tc.name, 
                            args=tc.arguments
                        ))
                if not parts:
                    parts.append(types.Part.from_text(text=" "))
                contents.append(types.Content(role="model", parts=parts))
            elif msg.is_tool():
                tool_name = self._find_tool_name(msg.tool_call_id, messages)
                parts = [
                    types.Part.from_function_response(
                        name=tool_name,
                        response={"result": msg.content}
                    )
                ]
                contents.append(types.Content(role="user", parts=parts))

        gemini_tools = self._get_gemini_tools()
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7,
            tools=gemini_tools if gemini_tools else None
        )

        try:
            # google-genai is synchronous mostly, but we can wrap or just call generate_content.
            # Using the sync client since 'async' methods might not be fully exposed transparently
            # or `aio` client is separate. For this technical test, we wrap the call.
            response = self.client.models.generate_content(
                model=self._model_name,
                contents=contents,
                config=config
            )
            
            tool_calls = []
            text_response = ""
            
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.text:
                        text_response += part.text
                    elif part.function_call:
                        # Gemini SDK maps function_call to an object
                        import uuid
                        call_id = str(uuid.uuid4())[:8] # Gemini rarely gives an explicit tool call ID, we mock one
                        tool_calls.append(ToolCall(
                            id=call_id,
                            name=part.function_call.name,
                            arguments=dict(part.function_call.args)
                        ))
                        
            return LLMResponse(content=text_response, tool_calls=tool_calls)

        except Exception as e:
            logger.error(f"Error invocando Gemini: {e}")
            raise LLMProviderError(f"Falla en comunicación con Gemini: {e}")
