from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .settings import settings
from ..persistence.database import get_db_session
from ..adapters.postgres_memory_adapter import PostgresMemoryAdapter
from ..adapters.gemini_llm_adapter import GeminiLLMAdapter
from ..adapters.mcp_client_adapter import MCPClientAdapter

from ...application.services.contextual_memory_manager import ContextualMemoryManager
from ...application.services.tool_dispatcher import ToolDispatcher
from ...application.use_cases.process_chat_message import ProcessChatMessageUseCase

# Instancias compartidas/Singletons donde aplique
mcp_adapter = MCPClientAdapter(
    command=settings.mcp_server_command,
    args=settings.mcp_server_args.split(";"),
    transport=settings.mcp_transport,
    sse_url=settings.mcp_sse_url
)

# El esquema de herramientas debería ser dinámico, se carga una vez idealmente
# O se define a mano para que el Agent siempre sepa que existen
AVAILABLE_TOOLS = [
    {
        "name": "search_knowledge_base",
        "description": "Busca en la base de conocimiento semántica documentos relevantes al texto provisto.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Consulta de búsqueda fáctica orientada a productos de Bancolombia"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_article_by_url",
        "description": "Recupera el contenido de un artículo específico dada su URL del sitio de Bancolombia.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL de la página de Bancolombia"}
            },
            "required": ["url"]
        }
    }
]

# Creamos el adapter con las API Keys correspondientes de Gemini
llm_adapter = GeminiLLMAdapter(
    api_key=settings.gemini_api_key, 
    available_tools_schema=AVAILABLE_TOOLS
)
tool_dispatcher = ToolDispatcher(mcp_adapter)
llm_orchestrator = None # Resolver import circular en __init__ o injectado
from ...application.services.llm_orchestrator import LLMOrchestrator
llm_orchestrator = LLMOrchestrator(llm_port=llm_adapter, tool_dispatcher=tool_dispatcher)


async def get_memory_manager(session: AsyncSession = Depends(get_db_session)):
    memory_port = PostgresMemoryAdapter(session)
    return ContextualMemoryManager(memory_port=memory_port)

async def get_chat_use_case(memory_manager: ContextualMemoryManager = Depends(get_memory_manager)):
    return ProcessChatMessageUseCase(
        memory_manager=memory_manager,
        orchestrator=llm_orchestrator,
        max_context_window=10
    )
