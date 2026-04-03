from ..dto.chat_dto import ChatRequestDTO, ChatResponseDTO
from ..services.contextual_memory_manager import ContextualMemoryManager
from ..services.llm_orchestrator import LLMOrchestrator
from ...domain.entities.message import Message
import logging

logger = logging.getLogger(__name__)

class ProcessChatMessageUseCase:
    """
    Caso de uso primario que ensambla la lógica desde el request del usuario
    hasta entregarle la respuesta final y guardar el historial.
    """
    def __init__(self, memory_manager: ContextualMemoryManager, orchestrator: LLMOrchestrator, max_context_window: int = 15):
        self.memory_manager = memory_manager
        self.orchestrator = orchestrator
        self.max_context_window = max_context_window

    async def execute(self, request: ChatRequestDTO) -> ChatResponseDTO:
        session_id = request.session_id
        user_text = request.message
        
        logger.info(f"Procesando mensaje para session_id: {session_id}")
        
        # 1. Recuperar conversación (crea si no existe)
        conversation = await self.memory_manager.get_or_create_conversation(session_id)
        
        # 2. Agregar el nuevo mensaje del usuario
        user_message = Message(role="user", content=user_text)
        await self.memory_manager.add_message(session_id, user_message)
        conversation.add_message(user_message)
        
        # 3. Obtener ventana de contexto (Memoria Corto Plazo)
        context_window = conversation.get_context_window(self.max_context_window)
        
        # 4. Orquestar el flujo LLM + MCP Tools
        final_reply, sources = await self.orchestrator.generate_final_response(context_window)
        
        # 5. Guardar la respuesta del assistant
        assistant_message = Message(role="assistant", content=final_reply)
        await self.memory_manager.add_message(session_id, assistant_message)
        
        # 6. Responder
        return ChatResponseDTO(reply=final_reply, sources=sources)
