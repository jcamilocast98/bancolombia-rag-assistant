from typing import List, Optional
from ...domain.ports.llm_port import LLMPort
from ...domain.entities.message import Message
from ...domain.entities.tool_call import ToolCall
from .tool_dispatcher import ToolDispatcher
import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_TEMPLATE = """
Eres un Asistente Virtual exclusivo del Grupo Bancolombia. Tu objetivo es ayudar a los clientes y usuarios a entender los productos y servicios del banco.
Debes adherirte a las siguientes reglas estrictas:
1. DEBES interactuar de forma educada, conversacional y servicial.
2. OUT-OF-SCOPE LIMITATION: SOLO puedes responder preguntas relacionadas con Bancolombia, sus productos, economía y procesos afines. Si el usuario pregunta por política, chistes, o cualquier otro banco/empresa, debes rechazar cortésmente la solicitud diciendo que como Asistente de Bancolombia, no estás autorizado a hablar de esos temas.
3. USO DE HERRAMIENTAS: Para responder preguntas fácticas sobre Bancolombia, DEBES llamar a la herramienta 'search_knowledge_base' INMEDIATAMENTE. NO preguntes permiso al usuario para buscar; hazlo directamente para proporcionar una respuesta informada.
4. CITAS OBLIGATORIAS: Al final de tu respuesta, DEBES listar las fuentes (URLs) encontradas.
5. EFICIENCIA: Sé directo y profesional. Si no encuentras información tras buscar, indícalo claramente.
6. Historial a continuación:
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
        # Reducimos iteraciones para ahorrar cuota de API (2 por pregunta)
        max_iterations = 2
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
