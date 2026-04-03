from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from .database import Base

class ConversationModel(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    messages = relationship("MessageModel", back_populates="conversation", order_by="MessageModel.created_at", cascade="all, delete-orphan")

class MessageModel(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    tool_calls = Column(JSON, nullable=True) # Guarda info JSON de tools referenciados
    tool_call_id = Column(String, nullable=True) # ID Referencia si es info devuelta por el MCP
    
    conversation = relationship("ConversationModel", back_populates="messages")
