from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from .base import Base


class ChatMessage(Base):
    """
    Chat message history for tracking user conversations with the AI.

    Each message represents either:
    - User input (prompt)
    - AI response (visualization spec)
    """
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True, index=True)

    # Message content
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)  # User prompt or AI explanation

    # If this was a visualization request
    visualization_spec = Column(JSONB, nullable=True)  # The actual visual spec if role='assistant'

    # Metadata
    interpreter_source = Column(String(50), nullable=True)  # 'llm', 'rules', 'image', 'fallback'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", backref="chat_messages")
    workspace = relationship("Workspace", backref="chat_messages")

    # Indexes for efficient queries
    __table_args__ = (
        Index('idx_chat_user_created', 'user_id', 'created_at'),  # "My recent chats"
        Index('idx_chat_workspace', 'workspace_id', 'created_at'),  # "Chat for this workspace"
    )
