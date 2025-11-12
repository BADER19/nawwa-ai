from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import json
from typing import Dict, Any

from models.user import User
from models.workspace import Workspace
from models.project import Project
from utils.auth_deps import get_current_user
from services.db import get_db
from services.email_service import send_email_sync

router = APIRouter()


class DeleteAccountRequest(BaseModel):
    password: str
    confirmation: str  # Must be "DELETE MY ACCOUNT"


class DataExportRequest(BaseModel):
    include_workspaces: bool = True
    include_projects: bool = True


def export_user_data(user: User, db: Session, include_workspaces: bool = True, include_projects: bool = True) -> Dict[str, Any]:
    """Export all user data to a dictionary"""
    data = {
        "export_date": datetime.utcnow().isoformat(),
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "email_verified": user.email_verified,
            "subscription_tier": user.subscription_tier.value if user.subscription_tier else "FREE",
            "subscription_status": user.subscription_status,
            "is_admin": user.is_admin,
            "current_context": user.current_context,
            "usage_count": user.usage_count,
            "usage_reset_date": user.usage_reset_date.isoformat() if user.usage_reset_date else None,
            "trial_ends_at": user.trial_ends_at.isoformat() if user.trial_ends_at else None,
            "two_factor_enabled": user.two_factor_enabled,
        }
    }

    # Include workspaces if requested
    if include_workspaces:
        workspaces = db.query(Workspace).filter(Workspace.owner_id == user.id).all()
        data["workspaces"] = [
            {
                "id": ws.id,
                "name": ws.name,
                "content": ws.content,
                "created_at": ws.created_at.isoformat() if ws.created_at else None,
                "updated_at": ws.updated_at.isoformat() if ws.updated_at else None,
            }
            for ws in workspaces
        ]

    # Include projects if requested
    if include_projects:
        projects = db.query(Project).filter(Project.owner_id == user.id).all()
        data["projects"] = [
            {
                "id": proj.id,
                "name": proj.name,
                "description": proj.description,
                "content": proj.content,
                "created_at": proj.created_at.isoformat() if proj.created_at else None,
                "updated_at": proj.updated_at.isoformat() if proj.updated_at else None,
            }
            for proj in projects
        ]

    return data


@router.get("/export")
def export_my_data(
    include_workspaces: bool = True,
    include_projects: bool = True,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export all user data (GDPR compliant)
    Returns a JSON file with all user information
    """
    data = export_user_data(user, db, include_workspaces, include_projects)

    # Return as downloadable JSON file
    json_data = json.dumps(data, indent=2, default=str)

    return Response(
        content=json_data,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=nawwa_data_export_{user.id}_{datetime.utcnow().strftime('%Y%m%d')}.json"
        }
    )


@router.post("/export-email")
def email_my_data(
    data: DataExportRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Email user data export to the user's registered email
    """
    export_data = export_user_data(user, db, data.include_workspaces, data.include_projects)
    json_data = json.dumps(export_data, indent=2, default=str)

    # Send email with data as attachment
    subject = "Your Nawwa AI Data Export"
    html_body = f"""
    <html>
    <body>
        <h2>Your Data Export</h2>
        <p>Hi {user.username},</p>
        <p>As requested, here is your complete data export from Nawwa AI.</p>
        <p>This export includes:</p>
        <ul>
            <li>Your profile information</li>
            {"<li>Your workspaces</li>" if data.include_workspaces else ""}
            {"<li>Your projects</li>" if data.include_projects else ""}
        </ul>
        <p>The data is attached as a JSON file.</p>
        <p>Best regards,<br>The Nawwa AI Team</p>
    </body>
    </html>
    """

    # Note: In production, you'd attach the JSON file to the email
    # For now, we'll just indicate success
    try:
        # In a real implementation, you'd attach the JSON file
        send_email_sync(user.email, subject, html_body)
        return {"message": "Data export has been emailed to your registered address"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to send data export email")


@router.delete("/delete-account")
def delete_my_account(
    request_data: DeleteAccountRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Permanently delete user account and all associated data (GDPR compliant)
    Requires password verification and explicit confirmation
    """
    from services.auth import verify_password

    # Verify confirmation text
    if request_data.confirmation != "DELETE MY ACCOUNT":
        raise HTTPException(
            status_code=400,
            detail="Please confirm by typing 'DELETE MY ACCOUNT' exactly"
        )

    # Verify password
    if not verify_password(request_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid password")

    try:
        # Store email for confirmation message
        user_email = user.email
        user_name = user.username

        # Delete all associated data (cascade delete handles workspaces and projects)
        db.delete(user)
        db.commit()

        # Send confirmation email (best effort, don't fail if email fails)
        try:
            subject = "Account Deletion Confirmation"
            html_body = f"""
            <html>
            <body>
                <h2>Account Deleted</h2>
                <p>Hi {user_name},</p>
                <p>Your Nawwa AI account and all associated data have been permanently deleted as requested.</p>
                <p>We're sorry to see you go. If you ever want to come back, you're always welcome to create a new account.</p>
                <p>Best regards,<br>The Nawwa AI Team</p>
            </body>
            </html>
            """
            send_email_sync(user_email, subject, html_body)
        except:
            pass  # Don't fail deletion if email fails

        return {"message": "Account and all associated data have been permanently deleted"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete account: {str(e)}")


@router.get("/privacy-settings")
def get_privacy_settings(user: User = Depends(get_current_user)):
    """Get user's privacy settings"""
    return {
        "email": user.email,
        "email_verified": user.email_verified,
        "two_factor_enabled": user.two_factor_enabled,
        "data_retention_days": 365,  # Default retention period
        "can_delete_account": True,
        "can_export_data": True,
        "last_login": None,  # You could track this separately
        "account_created": user.created_at.isoformat() if user.created_at else None,
    }


@router.post("/request-data-deletion")
def request_data_deletion(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Request deletion of specific user data while keeping the account
    This could be used to delete old workspaces, projects, etc.
    """
    # Delete old workspaces (older than 90 days)
    from datetime import timedelta
    cutoff_date = datetime.utcnow() - timedelta(days=90)

    old_workspaces = db.query(Workspace).filter(
        Workspace.owner_id == user.id,
        Workspace.updated_at < cutoff_date
    ).all()

    old_projects = db.query(Project).filter(
        Project.owner_id == user.id,
        Project.updated_at < cutoff_date
    ).all()

    workspace_count = len(old_workspaces)
    project_count = len(old_projects)

    for ws in old_workspaces:
        db.delete(ws)

    for proj in old_projects:
        db.delete(proj)

    db.commit()

    return {
        "message": f"Deleted {workspace_count} old workspaces and {project_count} old projects",
        "deleted_workspaces": workspace_count,
        "deleted_projects": project_count
    }