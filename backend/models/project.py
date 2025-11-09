from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Index, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from .base import Base


class Project(Base):
    """
    Context-aware project for organizing visualizations

    A project represents a specific use case with context:
    - Teacher preparing class materials
    - Business professional creating presentation
    - Student studying for exam
    - Researcher writing paper

    The context (role, audience, goal) helps the AI generate
    appropriate visualizations tailored to the user's needs.
    """
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Context fields for intelligent visualization
    user_role = Column(String(100), nullable=False)  # teacher, business, student, researcher
    audience = Column(String(100), nullable=False)   # students, executives, peers, self
    goal = Column(String(100), nullable=False)       # teach, present, learn, analyze
    setting = Column(String(100), nullable=False)    # classroom, boardroom, study, paper
    tone = Column(String(50), default="professional")  # simple, professional, academic, casual
    depth = Column(String(50), default="intermediate") # beginner, intermediate, expert

    # Additional context metadata (flexible JSON storage)
    context_metadata = Column(JSONB, default={})

    # Topics/content the user wants to cover
    topics = Column(JSONB, default=[])  # ["topic1", "topic2", ...]

    # Ownership
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="projects")
    visualizations = relationship("ProjectVisualization", back_populates="project", cascade="all, delete-orphan")

    # Table-level indexes and constraints
    __table_args__ = (
        Index('idx_project_owner_created', 'owner_id', 'created_at'),  # "My recent projects"
        Index('idx_project_owner_updated', 'owner_id', 'updated_at'),  # "My recently edited projects"
    )


class ProjectVisualization(Base):
    """
    Individual visualization within a project (like a slide in a presentation)
    """
    __tablename__ = "project_visualizations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    # Ordering and organization
    slide_number = Column(Integer, nullable=False)  # Order in the project
    title = Column(String(255), nullable=False)

    # Visualization data
    data = Column(JSONB, nullable=False)  # The plotlySpec or other visualization data

    # Additional metadata
    speaker_notes = Column(Text, nullable=True)  # For presentations
    annotations = Column(JSONB, default=[])      # Key insights to highlight

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="visualizations")

    # Table-level constraints and indexes
    __table_args__ = (
        UniqueConstraint('project_id', 'slide_number', name='uq_project_slide_number'),  # Prevent duplicate slide numbers
        CheckConstraint('slide_number >= 1', name='check_slide_number_positive'),  # Slide numbers must be positive
        Index('idx_project_viz_project_slide', 'project_id', 'slide_number'),  # For ordered retrieval
    )
