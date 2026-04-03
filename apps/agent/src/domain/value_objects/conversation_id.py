from pydantic import RootModel
import uuid

class ConversationId(RootModel[str]):
    """
    Value Object para representar el ID de una conversación,
    garantizando que siga el formato estándar UUID (u otro definido).
    """

    @classmethod
    def generate(cls) -> "ConversationId":
        return cls(str(uuid.uuid4()))
