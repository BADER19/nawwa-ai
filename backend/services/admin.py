"""
Admin service for comprehensive system management.
Provides full CRUD operations for users, workspaces, projects, and chat history.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr

from services.db import get_db
from models.user import User, SubscriptionTier
from models.workspace import Workspace
from models.project import Project
from models.chat_message import ChatMessage
from utils.auth_deps import get_admin_user


router = APIRouter()


# ==================== ADMIN ROOT ====================

@router.get("/")
async def admin_root(admin: User = Depends(get_admin_user)):
    """
    Admin panel welcome - lists all available admin endpoints.
    """
    return {
        "message": f"Welcome to Nawwa Admin Panel, {admin.username}!",
        "admin_email": admin.email,
        "endpoints": {
            "users": {
                "list": "GET /admin/users - List all users (filters: tier, is_admin, search)",
                "get": "GET /admin/users/{id} - Get user details",
                "update": "PUT /admin/users/{id} - Update user (tier, admin status, quota, etc.)",
                "delete": "DELETE /admin/users/{id} - Delete user",
                "reset_quota": "POST /admin/users/{id}/reset-quota - Reset user's daily quota"
            },
            "workspaces": {
                "list": "GET /admin/workspaces - List all workspaces (filter: owner_id)",
                "get": "GET /admin/workspaces/{id} - Get workspace details",
                "delete": "DELETE /admin/workspaces/{id} - Delete workspace"
            },
            "projects": {
                "list": "GET /admin/projects - List all projects (filter: owner_id)",
                "get": "GET /admin/projects/{id} - Get project details",
                "delete": "DELETE /admin/projects/{id} - Delete project"
            },
            "chat_history": {
                "list": "GET /admin/chat-history - List chat messages (filter: user_id, workspace_id)",
                "delete": "DELETE /admin/chat-history/{id} - Delete chat message"
            },
            "stats": "GET /admin/stats - System-wide statistics and analytics"
        },
        "quick_actions": {
            "upgrade_user_to_pro": "PUT /admin/users/{id} with body: {\"subscription_tier\": \"PRO\"}",
            "make_user_admin": "PUT /admin/users/{id} with body: {\"is_admin\": true}",
            "reset_user_quota": "POST /admin/users/{id}/reset-quota"
        },
        "docs": "http://localhost:28001/docs - Full API documentation"
    }


# ==================== PYDANTIC MODELS ====================

class UserListResponse(BaseModel):
    id: int
    email: str
    username: str
    subscription_tier: str
    is_admin: bool
    created_at: datetime
    usage_count: int
    usage_reset_date: datetime


class UserDetailResponse(BaseModel):
    id: int
    email: str
    username: str
    subscription_tier: str
    is_admin: bool
    created_at: datetime
    usage_count: int
    usage_reset_date: datetime
    paypal_subscription_id: Optional[str]
    paypal_payer_id: Optional[str]
    subscription_status: str
    current_context: Optional[str]
    trial_ends_at: Optional[datetime]


class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    subscription_tier: Optional[SubscriptionTier] = None
    is_admin: Optional[bool] = None
    usage_count: Optional[int] = None


class WorkspaceListResponse(BaseModel):
    id: int
    name: str
    owner_id: int
    owner_email: str
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(BaseModel):
    id: int
    name: str
    owner_id: int
    owner_email: str
    created_at: datetime
    updated_at: datetime


class ChatMessageResponse(BaseModel):
    id: int
    user_id: int
    user_email: str
    workspace_id: Optional[int]
    message: str
    response: Optional[str]
    created_at: datetime


class SystemStatsResponse(BaseModel):
    total_users: int
    total_admins: int
    total_workspaces: int
    total_projects: int
    total_chat_messages: int
    users_by_tier: dict
    new_users_last_30_days: int
    active_users_last_7_days: int


# ==================== USER MANAGEMENT ====================

@router.get("/users", response_model=List[UserListResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    tier: Optional[SubscriptionTier] = None,
    is_admin: Optional[bool] = None,
    search: Optional[str] = None,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    List all users with pagination and filters.
    Search by email or username.
    """
    query = db.query(User)

    if tier:
        query = query.filter(User.subscription_tier == tier)

    if is_admin is not None:
        query = query.filter(User.is_admin == is_admin)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (User.email.ilike(search_pattern)) | (User.username.ilike(search_pattern))
        )

    query = query.order_by(desc(User.created_at))
    users = query.offset(skip).limit(limit).all()

    return [
        UserListResponse(
            id=u.id,
            email=u.email,
            username=u.username,
            subscription_tier=u.subscription_tier.value,
            is_admin=u.is_admin,
            created_at=u.created_at,
            usage_count=u.usage_count,
            usage_reset_date=u.usage_reset_date
        )
        for u in users
    ]


@router.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserDetailResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        subscription_tier=user.subscription_tier.value,
        is_admin=user.is_admin,
        created_at=user.created_at,
        usage_count=user.usage_count,
        usage_reset_date=user.usage_reset_date,
        paypal_subscription_id=user.paypal_subscription_id,
        paypal_payer_id=user.paypal_payer_id,
        subscription_status=user.subscription_status,
        current_context=user.current_context,
        trial_ends_at=user.trial_ends_at
    )


@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    update_data: UpdateUserRequest,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update user information.
    Admin can change tier, email, username, admin status, usage count, etc.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent admin from removing their own admin status
    if user.id == admin.id and update_data.is_admin is False:
        raise HTTPException(
            status_code=400,
            detail="Cannot remove admin status from yourself. Ask another admin."
        )

    # Apply updates
    if update_data.email is not None:
        # Check email uniqueness
        existing = db.query(User).filter(User.email == update_data.email, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = update_data.email

    if update_data.username is not None:
        user.username = update_data.username

    if update_data.subscription_tier is not None:
        user.subscription_tier = update_data.subscription_tier

    if update_data.is_admin is not None:
        user.is_admin = update_data.is_admin

    if update_data.usage_count is not None:
        user.usage_count = update_data.usage_count

    db.commit()
    db.refresh(user)

    return {
        "ok": True,
        "message": f"User {user.email} updated successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "subscription_tier": user.subscription_tier.value,
            "is_admin": user.is_admin
        }
    }


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete a user and all associated data (workspaces, projects, chat messages).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent admin from deleting themselves
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    email = user.email
    db.delete(user)
    db.commit()

    return {"ok": True, "message": f"User {email} and all associated data deleted"}


@router.post("/users/{user_id}/reset-quota")
async def reset_user_quota(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Reset a user's usage quota to 0."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.usage_count = 0
    user.usage_reset_date = datetime.utcnow() + timedelta(days=1)
    db.commit()

    return {"ok": True, "message": f"Quota reset for {user.email}"}


# ==================== WORKSPACE MANAGEMENT ====================

@router.get("/workspaces", response_model=List[WorkspaceListResponse])
async def list_workspaces(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    owner_id: Optional[int] = None,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """List all workspaces across the system."""
    query = db.query(Workspace).join(User, Workspace.owner_id == User.id)

    if owner_id:
        query = query.filter(Workspace.owner_id == owner_id)

    query = query.order_by(desc(Workspace.updated_at))
    workspaces = query.offset(skip).limit(limit).all()

    return [
        WorkspaceListResponse(
            id=w.id,
            name=w.name,
            owner_id=w.owner_id,
            owner_email=w.owner.email,
            created_at=w.created_at,
            updated_at=w.updated_at
        )
        for w in workspaces
    ]


@router.get("/workspaces/{workspace_id}")
async def get_workspace(
    workspace_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get workspace details including content."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return {
        "id": workspace.id,
        "name": workspace.name,
        "owner_id": workspace.owner_id,
        "owner_email": workspace.owner.email,
        "content": workspace.content,
        "created_at": workspace.created_at,
        "updated_at": workspace.updated_at
    }


@router.delete("/workspaces/{workspace_id}")
async def delete_workspace(
    workspace_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a workspace."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    name = workspace.name
    db.delete(workspace)
    db.commit()

    return {"ok": True, "message": f"Workspace '{name}' deleted"}


# ==================== PROJECT MANAGEMENT ====================

@router.get("/projects", response_model=List[ProjectListResponse])
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    owner_id: Optional[int] = None,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """List all projects across the system."""
    query = db.query(Project).join(User, Project.owner_id == User.id)

    if owner_id:
        query = query.filter(Project.owner_id == owner_id)

    query = query.order_by(desc(Project.updated_at))
    projects = query.offset(skip).limit(limit).all()

    return [
        ProjectListResponse(
            id=p.id,
            name=p.name,
            owner_id=p.owner_id,
            owner_email=p.owner.email,
            created_at=p.created_at,
            updated_at=p.updated_at
        )
        for p in projects
    ]


@router.get("/projects/{project_id}")
async def get_project(
    project_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get project details including description."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {
        "id": project.id,
        "name": project.name,
        "owner_id": project.owner_id,
        "owner_email": project.owner.email,
        "description": project.description,
        "created_at": project.created_at,
        "updated_at": project.updated_at
    }


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    name = project.name
    db.delete(project)
    db.commit()

    return {"ok": True, "message": f"Project '{name}' deleted"}


# ==================== CHAT HISTORY MANAGEMENT ====================

@router.get("/chat-history", response_model=List[ChatMessageResponse])
async def list_chat_messages(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    user_id: Optional[int] = None,
    workspace_id: Optional[int] = None,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """List chat messages with filters."""
    query = db.query(ChatMessage).join(User, ChatMessage.user_id == User.id)

    if user_id:
        query = query.filter(ChatMessage.user_id == user_id)

    if workspace_id:
        query = query.filter(ChatMessage.workspace_id == workspace_id)

    query = query.order_by(desc(ChatMessage.created_at))
    messages = query.offset(skip).limit(limit).all()

    return [
        ChatMessageResponse(
            id=m.id,
            user_id=m.user_id,
            user_email=m.user.email,
            workspace_id=m.workspace_id,
            message=m.message,
            response=m.response,
            created_at=m.created_at
        )
        for m in messages
    ]


@router.delete("/chat-history/{message_id}")
async def delete_chat_message(
    message_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a chat message."""
    message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Chat message not found")

    db.delete(message)
    db.commit()

    return {"ok": True, "message": "Chat message deleted"}


# ==================== SYSTEM STATISTICS ====================

@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive system statistics."""

    # Total counts
    total_users = db.query(func.count(User.id)).scalar()
    total_admins = db.query(func.count(User.id)).filter(User.is_admin == True).scalar()
    total_workspaces = db.query(func.count(Workspace.id)).scalar()
    total_projects = db.query(func.count(Project.id)).scalar()
    total_chat_messages = db.query(func.count(ChatMessage.id)).scalar()

    # Users by tier
    tier_counts = db.query(
        User.subscription_tier,
        func.count(User.id)
    ).group_by(User.subscription_tier).all()

    users_by_tier = {tier.value: count for tier, count in tier_counts}

    # New users in last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_users_last_30_days = db.query(func.count(User.id)).filter(
        User.created_at >= thirty_days_ago
    ).scalar()

    # Active users last 7 days (users who sent chat messages)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    active_users_last_7_days = db.query(func.count(func.distinct(ChatMessage.user_id))).filter(
        ChatMessage.created_at >= seven_days_ago
    ).scalar()

    return SystemStatsResponse(
        total_users=total_users,
        total_admins=total_admins,
        total_workspaces=total_workspaces,
        total_projects=total_projects,
        total_chat_messages=total_chat_messages,
        users_by_tier=users_by_tier,
        new_users_last_30_days=new_users_last_30_days,
        active_users_last_7_days=active_users_last_7_days
    )
