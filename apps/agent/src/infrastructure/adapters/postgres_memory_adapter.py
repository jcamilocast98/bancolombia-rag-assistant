from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...domain.ports.memory_port import MemoryPort
from ...domain.entities.conversation import Conversation
from ...domain.entities.message import Message
from ...domain.entities.tool_call import ToolCall
from ...domain.value_objects.conversation_id import ConversationId
from ..persistence.models import ConversationModel, MessageModel
import json

class PostgresMemoryAdapter(MemoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_conversation(self, conversation: Conversation) -> None:
        db_conv = await self.session.get(ConversationModel, str(conversation.id))
        if not db_conv:
            db_conv = ConversationModel(id=str(conversation.id))
            self.session.add(db_conv)
        await self.session.commit()

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        stmt = select(ConversationModel).where(ConversationModel.id == conversation_id)
        result = await self.session.execute(stmt)
        db_conv = result.scalars().first()
        
        if not db_conv:
            return None
            
        stmt_messages = select(MessageModel).where(MessageModel.conversation_id == conversation_id).order_by(MessageModel.created_at.asc())
        msg_result = await self.session.execute(stmt_messages)
        db_messages = msg_result.scalars().all()
        
        domain_messages = []
        for dm in db_messages:
            tool_calls = []
            if dm.tool_calls:
                # Decodificar el JSON de tool_calls
                for tc_dict in json.loads(dm.tool_calls):
                    tool_calls.append(ToolCall(**tc_dict))
            
            domain_messages.append(Message(
                role=dm.role,
                content=dm.content or "",
                created_at=dm.created_at,
                tool_calls=tool_calls if tool_calls else None,
                tool_call_id=dm.tool_call_id
            ))
            
        conv = Conversation(id=ConversationId(db_conv.id), messages=domain_messages, created_at=db_conv.created_at, updated_at=db_conv.updated_at)
        return conv

    async def add_message_to_conversation(self, conversation_id: str, message: Message) -> None:
        tool_calls_json = None
        if message.tool_calls:
            tool_calls_json = json.dumps([tc.model_dump() for tc in message.tool_calls])
            
        db_msg = MessageModel(
            conversation_id=conversation_id,
            role=message.role,
            content=message.content,
            created_at=message.created_at,
            tool_calls=tool_calls_json,
            tool_call_id=message.tool_call_id
        )
        self.session.add(db_msg)
        await self.session.commit()
