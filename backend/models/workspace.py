from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from .base import Base


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    data = Column(JSONB, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="workspaces")

    # Table-level indexes for common queries
    __table_args__ = (
        Index('idx_workspace_owner_created', 'owner_id', 'created_at'),  # "My recent workspaces"
        Index('idx_workspace_owner_updated', 'owner_id', 'updated_at'),  # "My recently edited workspaces"
    )
