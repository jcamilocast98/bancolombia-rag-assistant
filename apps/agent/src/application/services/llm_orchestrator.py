from typing import List, Optional
from ...domain.ports.llm_port import LLMPort
from ...domain.entities.message import Message
from ...domain.entities.tool_call import ToolCall
from .tool_dispatcher import ToolDispatcher
import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_TEMPLATE = """
Eres un asistente virtual experto y amable del Grupo Bancolombia. Tu objetivo principal es resolver las dudas de los usuarios sobre productos, servicios y trámites basándote ÚNICAMENTE en la información oficial proporcionada por tus herramientas.

CONTEXTO DEL SISTEMA:
- Tienes acceso a la herramienta técnica 'get_knowledge_base_stats'. Úsala si el usuario pregunta cuántos documentos tienes indexados, qué tan actualizada está tu información o qué modelo de IA utilizas. DEBES reportar todos los detalles técnicos que la herramienta te proporcione (total de documentos, fragmentos, fecha y modelo).

REGLAS DE USO DE HERRAMIENTAS:
1. Búsquedas Generales: Si el usuario hace una pregunta abierta (ej. "¿Cómo abro una cuenta de ahorros?" o "Requisitos para crédito hipotecario"), DEBES usar la herramienta 'search_knowledge_base' para buscar semánticamente la respuesta.
2. Lectura de Artículos Específicos: Si el usuario te proporciona una URL específica de Bancolombia o si en una búsqueda anterior encontraste una URL y necesitas más detalles para responder, DEBES usar la herramienta 'get_article_by_url' para leer el contenido completo de esa página.
3. Exploración de Temas: Si el usuario pregunta de qué temas le puedes hablar, qué información tienes disponible, o pide un resumen de tus conocimientos, DEBES usar la herramienta 'list_categories' para mostrarle las opciones disponibles.

REGLAS DE RESPUESTA:
- Si el usuario pregunta "ayuda" o "¿qué puedes hacer?", consulta primero 'list_categories' para dar una respuesta estructurada.
- Mantén un tono corporativo, seguro y útil, propio de Bancolombia.
- Al final de tu respuesta, DEBES listar las fuentes utilizadas en el formato: (URL, Título, Score de Relevancia) cuando provengan de una búsqueda.
- ✅ DEDUPLICACIÓN: Si una misma URL aparece varias veces en los resultados de la herramienta 'search_knowledge_base', DEBES listarla solo UNA vez en las fuentes finales, utilizando el Título más descriptivo y el Score de Relevancia más alto.
- IMPORTANTE: Extrae el Título y el Score de la información devuelta por la herramienta 'search_knowledge_base'.
- Ejemplo de cita: 
  Fuentes:
  * (https://www.bancolombia.com/personas/cuentas, Productos de ahorro y Cuentas, 0.9845)
  * (https://www.bancolombia.com/personas/bolsillos, Bolsillos Bancolombia, 0.7231)

- Si no encuentras información oficial, indícalo cortésmente y sugiere al usuario contactar los canales oficiales de Bancolombia.

Historial a continuación:
"""

class LLMOrchestrator:
    """
    Orquesta el flujo principal con el LLM: gestionando prompts, 
    iterando cuando se requiere llamar tools y componiendo la fuente.
    """
    def __init__(self, llm_port: LLMPort, tool_dispatcher: ToolDispatcher):
        self.llm_port = llm_port
        self.tool_dispatcher = tool_dispatcher

    async def generate_final_response(self, context_messages: List[Message]) -> tuple[str, List[str]]:
        """
        Ejecuta el bucle de razonamiento del LLM. Genera una respuesta, si el LLM
        pide una herramienta, se ejecuta y se vuelve al LLM, hasta tener la respuesta final.
        Devuelve (respuesta de texto, lista de fuentes).
        """
        working_messages = context_messages.copy()
        
        # Bucle de interacción con LLM para Tool Calling
        # Aumentamos a 5 para permitir busquedas más complejas y lectura de URLs
        max_iterations = 5
        iteration = 0
        all_sources = set()
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"LLM Orchestrator iteración {iteration}")
            
            # Invocar al modelo
            response = await self.llm_port.generate_response(SYSTEM_PROMPT_TEMPLATE, working_messages)
            
            if not response.requires_action():
                # Combinar fuentes detectadas por el adapter con las recolectadas
                combined_sources = list(set(response.sources or []) | all_sources)
                logger.info(f"Respuesta final generada: {response.content[:100]}...")
                return response.content, combined_sources
            
            # Agregar el mensaje de "Assistant" con las peticiones de herramientas al contexto en curso
            assistant_message = Message(
                role="assistant", 
                content=response.content,
                tool_calls=response.tool_calls
            )
            working_messages.append(assistant_message)
            
            # Procesar las herramientas y agregar la respuesta al historial para el siguiente ciclo
            for tool_call in response.tool_calls:
                result = await self.tool_dispatcher.execute_tool(tool_call)
                logger.info(f"Resultado de tool {tool_call.name}: {str(result)[:200]}...")
                # Añadir la respuesta del tool
                tool_message = Message(
                    role="tool",
                    content=result,
                    tool_call_id=tool_call.id
                )
                working_messages.append(tool_message)
                
        # Si sobrepasa iteraciones, retornar respuesta parcial
        logger.warning("Agent loop reached maximum iterations sin llegar a respuesta sin tool")
        return "Disculpa, he encontrado un problema procesando tu solicitud.", list(all_sources)
