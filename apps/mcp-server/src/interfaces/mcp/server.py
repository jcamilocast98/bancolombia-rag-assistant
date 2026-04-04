"""
Servidor MCP RAG — Bancolombia
Expone herramientas y recursos MCP para que el Agente acceda a la base de conocimiento.
"""
import json
import logging
from mcp.server import Server
from mcp.types import TextContent, Tool, Resource

from src.infrastructure.adapters.pgvector_adapter import PgVectorAdapter
from src.infrastructure.adapters.gemini_embedding_adapter import GeminiEmbeddingAdapter
from src.application.use_cases.search_knowledge_base import SearchKnowledgeBase
from src.application.use_cases.get_article_by_url import GetArticleByUrl
from src.application.use_cases.get_knowledge_base_stats import GetKnowledgeBaseStats

logger = logging.getLogger(__name__)

# Instanciar adaptadores
vector_db = PgVectorAdapter()
embedding_adapter = GeminiEmbeddingAdapter()

# Instanciar casos de uso
search_uc = SearchKnowledgeBase(vector_db=vector_db, embedding_adapter=embedding_adapter)
article_uc = GetArticleByUrl(vector_db=vector_db)
stats_uc = GetKnowledgeBaseStats(vector_db=vector_db)

# Crear servidor MCP
mcp_server = Server("bancolombia-rag-mcp")


@mcp_server.list_tools()
async def list_tools():
    """Registra las herramientas disponibles."""
    return [
        Tool(
            name="search_knowledge_base",
            description=(
                "Busca en la base de conocimiento de Bancolombia Personas usando búsqueda semántica. "
                "Retorna los fragmentos de texto más relevantes con sus URLs fuente."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Consulta de búsqueda en lenguaje natural sobre productos/servicios de Bancolombia",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Número máximo de resultados a retornar (default: 5)",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_article_by_url",
            description=(
                "Recupera el contenido completo de un artículo específico dada su URL del sitio de Bancolombia. "
                "Reconstruye el texto completo a partir de los fragmentos indexados."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL completa de la página de Bancolombia (ej: https://www.bancolombia.com/personas/cuentas)",
                    }
                },
                "required": ["url"],
            },
        ),
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Ejecuta una herramienta MCP."""
    logger.info(f"[MCP] Tool call: {name} args={arguments}")

    if name == "search_knowledge_base":
        query = arguments.get("query", "")
        top_k = arguments.get("top_k", 5)

        result = await search_uc.execute(query=query, top_k=top_k)

        if not result.chunks:
            return [TextContent(type="text", text="No se encontraron resultados para la consulta.")]

        output_parts = []
        for i, chunk in enumerate(result.chunks, 1):
            output_parts.append(
                f"--- Resultado {i} ---\n"
                f"URL: {chunk.url}\n"
                f"Contenido: {chunk.content}\n"
            )

        header = f"Se encontraron {result.total_results} resultados (método: {result.search_method}):\n\n"
        return [TextContent(type="text", text=header + "\n".join(output_parts))]

    elif name == "get_article_by_url":
        url = arguments.get("url", "")
        result = await article_uc.execute(url=url)

        if "error" in result and result.get("chunks_count", 0) == 0:
            return [TextContent(type="text", text=result["error"])]

        text = (
            f"Artículo recuperado de: {result['url']}\n"
            f"Fragmentos: {result['chunks_count']}\n\n"
            f"{result['content']}"
        )
        return [TextContent(type="text", text=text)]

    else:
        return [TextContent(type="text", text=f"Herramienta desconocida: {name}")]


@mcp_server.list_resources()
async def list_resources():
    """Registra los recursos disponibles."""
    return [
        Resource(
            uri="knowledge-base://stats",
            name="Estadísticas de la Base de Conocimiento",
            description="Retorna estadísticas de la KB: total de documentos, chunks, última actualización.",
            mimeType="application/json",
        )
    ]


@mcp_server.read_resource()
async def read_resource(uri: str):
    """Lee un recurso MCP."""
    if str(uri) == "knowledge-base://stats":
        stats = await stats_uc.execute()
        return stats.model_dump_json()
    
    return json.dumps({"error": f"Recurso no encontrado: {uri}"})
