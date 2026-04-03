from abc import ABC, abstractmethod

class ChatServicePort(ABC):
    """
    Puerto que expone los casos de uso hacia las interfaces externas
    para procesar los mensajes.
    """
    @abstractmethod
    async def process_message(self, session_id: str, message_content: str) -> dict:
        """
        Procesa el mensaje del usuario y devuelve la respuesta.
        """
        pass
