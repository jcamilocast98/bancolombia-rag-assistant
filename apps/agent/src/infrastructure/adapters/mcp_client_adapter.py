import json
import logging
from typing import List, Dict, Any
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

from ...domain.ports.mcp_client_port import MCPClientPort
from ...domain.exceptions.mcp_exceptions import MCPConnectionError, MCPExecutionError

logger = logging.getLogger(__name__)

class MCPClientAdapter(MCPClientPort):
    def __init__(self, command: str, args: List[str], transport: str = "stdio", sse_url: str = ""):
        """
        Adaptador MCP Client compatible con stdio y SSE.
        """
        self.command = command
        self.args = args
        self.transport = transport
        self.sse_url = sse_url
        
    async def _run_tool_stdio(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Ejecución vía stdio (proceso local)."""
        server_params = StdioServerParameters(
            command=self.command,
            args=self.args,
            env=None
        )
        
        async with AsyncExitStack() as stack:
            try:
                stdio_transport = await stack.enter_async_context(stdio_client(server_params))
                read, write = stdio_transport
                session = await stack.enter_async_context(ClientSession(read, write))
                await session.initialize()
                
                result = await session.call_tool(tool_name, arguments)
                if hasattr(result, 'content') and len(result.content) > 0:
                     return result.content[0].text
                return json.dumps({"status": "executed_empty_content"})
                
            except Exception as e:
                logger.error(f"Falla conexión Stdio MCP: {e}")
                raise MCPExecutionError(f"Error MCP stdio: {e}")

    async def _run_tool_sse(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Ejecución vía SSE (HTTP remoto)."""
        if not self.sse_url:
            raise MCPConnectionError("Configuración SSE faltante: mcp_sse_url no definida.")
            
        async with AsyncExitStack() as stack:
            try:
                read, write = await stack.enter_async_context(sse_client(self.sse_url))
                logger.info(f"[MCP-Client] Conexión SSE establecida con {self.sse_url}")
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    logger.info(f"[MCP-Client] Sesión MCP inicializada. Llamando a '{tool_name}'...")
                    
                    result = await session.call_tool(tool_name, arguments)
                    
                    if hasattr(result, 'isError') and result.isError:
                        logger.error(f"[MCP-Client] Error retornado por la herramienta: {result}")
                        return json.dumps({"error": "tool_execution_failed", "details": str(result)})

                    if hasattr(result, 'content') and len(result.content) > 0:
                        logger.info(f"[MCP-Client] Respuesta recibida de '{tool_name}' ({len(result.content[0].text)} caracteres)")
                        return result.content[0].text
                    
                    logger.warning(f"[MCP-Client] La herramienta '{tool_name}' retornó contenido vacío.")
                    return json.dumps({"status": "executed_empty_content"})
                
            except Exception as e:
                logger.error(f"Falla conexión SSE MCP en {self.sse_url}: {e}")
                raise MCPConnectionError(f"Error MCP SSE: {e}")

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Punto de entrada para llamar herramientas MCP."""
        logger.info(f"[MCP-Client] Llamando tool '{tool_name}' via {self.transport}")
        
        if self.transport.lower() == "sse":
            return await self._run_tool_sse(tool_name, arguments)
        return await self._run_tool_stdio(tool_name, arguments)

    async def get_tools_list(self) -> List[Dict[str, Any]]:
        """Descubre herramientas expuestas por el Servidor MCP."""
        async with AsyncExitStack() as stack:
            try:
                if self.transport.lower() == "sse":
                    if not self.sse_url: return []
                    read, write = await stack.enter_async_context(sse_client(self.sse_url))
                else:
                    server_params = StdioServerParameters(command=self.command, args=self.args)
                    read, write = await stack.enter_async_context(stdio_client(server_params))
                
                session = await stack.enter_async_context(ClientSession(read, write))
                await session.initialize()
                response = await session.list_tools()
                
                tools_schema = []
                for tool in response.tools:
                    tools_schema.append({
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.inputSchema
                    })
                return tools_schema
            except Exception as e:
                logger.warning(f"No se pudieron listar herramientas MCP ({self.transport}): {e}")
                return []
