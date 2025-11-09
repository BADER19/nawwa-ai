from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, CheckConstraint, Index, Boolean
from sqlalchemy.orm import relationship
import enum

from .base import Base


class SubscriptionTier(str, enum.Enum):
    FREE = "FREE"
    PRO = "PRO"
    TEAM = "TEAM"
    ENTERPRISE = "ENTERPRISE"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False, index=True)

    # User context for AI visualization
    current_context = Column(String(500), nullable=True)  # What user is working on today

    # Subscription fields
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False)
    paypal_subscription_id = Column(String(255), nullable=True, unique=True, index=True)  # PayPal billing agreement ID
    paypal_payer_id = Column(String(255), nullable=True, index=True)  # PayPal payer ID
    subscription_status = Column(String(50), default="active", nullable=False)  # active, suspended, cancelled, past_due, etc.

    # Usage tracking
    usage_count = Column(Integer, default=0, nullable=False)  # Visualizations this period
    usage_reset_date = Column(DateTime, default=datetime.utcnow, nullable=False)  # When to reset usage

    # Trial tracking
    trial_ends_at = Column(DateTime, nullable=True)

    workspaces = relationship("Workspace", back_populates="owner", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")

    # Table-level constraints
    __table_args__ = (
        CheckConstraint('usage_count >= 0', name='check_usage_count_non_negative'),
        CheckConstraint("subscription_status IN ('active', 'cancelled', 'suspended', 'past_due', 'pending', 'expired')",
                       name='check_valid_subscription_status'),
        Index('idx_user_created_at', 'created_at'),  # For sorting/filtering by signup date
        Index('idx_user_tier_status', 'subscription_tier', 'subscription_status'),  # For admin queries
    )

