import json
import logging
from typing import List, Dict, Any
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from ...domain.ports.mcp_client_port import MCPClientPort
from ...domain.exceptions.mcp_exceptions import MCPConnectionError, MCPExecutionError

logger = logging.getLogger(__name__)

class MCPClientAdapter(MCPClientPort):
    def __init__(self, command: str, args: List[str], transport: str = "stdio", sse_url: str = ""):
        self.command = command
        self.args = args
        self.transport = transport
        self.sse_url = sse_url
        
    async def _run_tool_stdio(self, tool_name: str, arguments: Dict[str, Any]) -> str:
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
                # Parsear la respuesta del SDK MCP que típicamente retorna content
                if hasattr(result, 'content') and len(result.content) > 0:
                     return result.content[0].text
                return json.dumps({"status": "executed_empty_content"})
                
            except Exception as e:
                logger.error(f"Falla conexión Stdio MCP: {e}")
                raise MCPExecutionError(f"Error MCP stdio: {e}")

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        if self.transport.lower() == "stdio":
            return await self._run_tool_stdio(tool_name, arguments)
        else:
            # Placeholder para SSE para implementaciones futuras
            raise NotImplementedError("Transporte SSE no está implementado aún en el adapter MVP")

    async def get_tools_list(self) -> List[Dict[str, Any]]:
        """Descubre tools expuestos por el MCP server"""
        if self.transport.lower() == "stdio":
            server_params = StdioServerParameters(command=self.command, args=self.args, env=None)
            async with AsyncExitStack() as stack:
                stdio_transport = await stack.enter_async_context(stdio_client(server_params))
                read, write = stdio_transport
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
        return []
