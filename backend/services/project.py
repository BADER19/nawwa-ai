from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from models.project import Project, ProjectVisualization
from models.user import User
from utils.schema_validators import ProjectCreate, ProjectOut, ProjectVisualizationOut
from utils.auth_deps import get_current_user
from services.db import get_db

router = APIRouter(prefix="/project", tags=["projects"])


@router.post("/", response_model=ProjectOut)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Create a new context-aware project
    """
    db_project = Project(
        name=project.name,
        description=project.description,
        user_role=project.user_role,
        audience=project.audience,
        goal=project.goal,
        setting=project.setting,
        tone=project.tone,
        depth=project.depth,
        context_metadata=project.context_metadata,
        topics=project.topics,
        owner_id=user.id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.get("/", response_model=List[ProjectOut])
def list_projects(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    List all projects for the current user
    """
    projects = db.query(Project).filter(Project.owner_id == user.id).order_by(Project.updated_at.desc()).all()
    return projects


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Get a specific project by ID
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    project_update: ProjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Update a project
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Update fields
    project.name = project_update.name
    project.description = project_update.description
    project.user_role = project_update.user_role
    project.audience = project_update.audience
    project.goal = project_update.goal
    project.setting = project_update.setting
    project.tone = project_update.tone
    project.depth = project_update.depth
    project.context_metadata = project_update.context_metadata
    project.topics = project_update.topics

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Delete a project
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}


@router.get("/{project_id}/visualizations", response_model=List[ProjectVisualizationOut])
def get_project_visualizations(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Get all visualizations for a project
    """
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    visualizations = db.query(ProjectVisualization).filter(
        ProjectVisualization.project_id == project_id
    ).order_by(ProjectVisualization.slide_number).all()

    return visualizations
