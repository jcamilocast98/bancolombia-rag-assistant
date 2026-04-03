from ...domain.ports.mcp_client_port import MCPClientPort
from ...domain.entities.tool_call import ToolCall
from ...domain.exceptions.mcp_exceptions import MCPExecutionError
import json
import logging

logger = logging.getLogger(__name__)

class ToolDispatcher:
    """
    Servicio encargado de enrutar las llamadas del LLM hacia el servidor MCP pertinente.
    """
    def __init__(self, mcp_client: MCPClientPort):
        self.mcp_client = mcp_client

    async def execute_tool(self, tool_call: ToolCall) -> str:
        """
        Ejecuta la herramienta indicada y devuelve el resultado como string JSON (o un mensaje de error).
        """
        try:
            logger.info(f"Ejecutando tool: {tool_call.name} con params: {tool_call.arguments}")
            result = await self.mcp_client.call_tool(tool_call.name, tool_call.arguments)
            tool_call.set_result(result)
            return result
        except Exception as e:
            logger.error(f"Error al ejecutar herramienta {tool_call.name}: {e}")
            error_msg = json.dumps({"error": str(e)})
            tool_call.set_result(error_msg)
            return error_msg
