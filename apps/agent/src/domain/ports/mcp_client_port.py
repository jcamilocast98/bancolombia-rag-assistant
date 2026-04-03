from typing import List, Dict, Any
from abc import ABC, abstractmethod

class MCPClientPort(ABC):
    """
    Puerto para la comunicación con herramientas de servidor MCP.
    """
    @abstractmethod
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Ejecuta una herramienta específica expuesta por el MCP server 
        (ej: 'search_knowledge_base') y retorna su resultado en formato String JSON.
        """
        pass
        
    @abstractmethod
    async def get_tools_list(self) -> List[Dict[str, Any]]:
        """
        Recupera dinámicamente las herramientas y metadatos (descripción, parámetros)
        disponibles en el MCP server con el que está conectado el agente.
        """
        pass
