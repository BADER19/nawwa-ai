from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from .base import Base


class AuditLog(Base):
    """Track all admin and sensitive user actions for security and compliance"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Who performed the action
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user_email = Column(String(255), nullable=False)  # Store email in case user is deleted
    user_role = Column(String(50), nullable=False)  # ADMIN, USER, etc.

    # What action was performed
    action = Column(String(100), nullable=False, index=True)  # e.g., "user.update", "subscription.change"
    resource_type = Column(String(50), nullable=False)  # e.g., "user", "workspace", "subscription"
    resource_id = Column(String(100), nullable=True)  # ID of the affected resource

    # Details of the action
    method = Column(String(10), nullable=False)  # HTTP method: GET, POST, PUT, DELETE
    endpoint = Column(String(255), nullable=False)  # API endpoint called
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)  # Browser/client info

    # What changed (for updates)
    old_values = Column(JSON, nullable=True)  # Previous state
    new_values = Column(JSON, nullable=True)  # New state
    changes = Column(JSON, nullable=True)  # Just the differences

    # Additional context
    status_code = Column(Integer, nullable=False)  # HTTP response code
    error_message = Column(Text, nullable=True)  # If action failed
    notes = Column(Text, nullable=True)  # Any additional notes

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])