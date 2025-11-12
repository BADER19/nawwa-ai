from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from fastapi import Request
import json
import logging

from models.audit_log import AuditLog
from models.user import User

logger = logging.getLogger("audit")


def log_action(
    db: Session,
    user: User,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    request: Optional[Request] = None,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    status_code: int = 200,
    error_message: Optional[str] = None,
    notes: Optional[str] = None
) -> AuditLog:
    """
    Log an action to the audit trail

    Args:
        db: Database session
        user: User performing the action
        action: Action identifier (e.g., "user.update", "subscription.change")
        resource_type: Type of resource (e.g., "user", "workspace")
        resource_id: ID of the resource being acted upon
        request: FastAPI request object (for IP, user agent, etc.)
        old_values: Previous state (for updates)
        new_values: New state (for updates)
        status_code: HTTP status code
        error_message: Error message if action failed
        notes: Additional notes
    """
    try:
        # Calculate changes if both old and new values provided
        changes = None
        if old_values and new_values:
            changes = {}
            for key in new_values:
                if key in old_values and old_values[key] != new_values[key]:
                    changes[key] = {
                        "old": old_values[key],
                        "new": new_values[key]
                    }

        # Extract request details
        ip_address = None
        user_agent = None
        method = "UNKNOWN"
        endpoint = ""

        if request:
            # Get IP address
            ip_address = request.client.host if request.client else None
            # Get user agent
            user_agent = request.headers.get("user-agent", "")
            # Get method and path
            method = request.method
            endpoint = str(request.url.path)

        # Create audit log entry
        audit_entry = AuditLog(
            user_id=user.id,
            user_email=user.email,
            user_role="ADMIN" if user.is_admin else "USER",
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            method=method,
            endpoint=endpoint,
            ip_address=ip_address,
            user_agent=user_agent,
            old_values=old_values,
            new_values=new_values,
            changes=changes,
            status_code=status_code,
            error_message=error_message,
            notes=notes,
            created_at=datetime.utcnow()
        )

        db.add(audit_entry)
        db.commit()

        logger.info(f"Audit log created: {action} by {user.email} on {resource_type}/{resource_id}")

        return audit_entry

    except Exception as e:
        logger.error(f"Failed to create audit log: {str(e)}")
        # Don't fail the main operation if audit logging fails
        db.rollback()
        return None


def log_admin_action(
    db: Session,
    admin: User,
    action: str,
    target_user: Optional[User] = None,
    request: Optional[Request] = None,
    changes: Optional[Dict[str, Any]] = None,
    notes: Optional[str] = None
) -> AuditLog:
    """
    Convenience function for logging admin actions on users

    Args:
        db: Database session
        admin: Admin user performing the action
        action: Action identifier
        target_user: User being acted upon
        request: FastAPI request object
        changes: What changed
        notes: Additional notes
    """
    resource_id = str(target_user.id) if target_user else None

    # Build old and new values from changes
    old_values = {}
    new_values = {}
    if changes:
        for key, value in changes.items():
            if isinstance(value, dict) and "old" in value and "new" in value:
                old_values[key] = value["old"]
                new_values[key] = value["new"]
            else:
                new_values[key] = value

    return log_action(
        db=db,
        user=admin,
        action=f"admin.{action}",
        resource_type="user",
        resource_id=resource_id,
        request=request,
        old_values=old_values if old_values else None,
        new_values=new_values if new_values else None,
        notes=notes
    )


def get_user_audit_logs(
    db: Session,
    user_id: int,
    limit: int = 100,
    offset: int = 0
) -> List[AuditLog]:
    """Get audit logs for a specific user"""
    return db.query(AuditLog)\
        .filter(AuditLog.user_id == user_id)\
        .order_by(AuditLog.created_at.desc())\
        .limit(limit)\
        .offset(offset)\
        .all()


def get_resource_audit_logs(
    db: Session,
    resource_type: str,
    resource_id: str,
    limit: int = 100,
    offset: int = 0
) -> List[AuditLog]:
    """Get audit logs for a specific resource"""
    return db.query(AuditLog)\
        .filter(
            AuditLog.resource_type == resource_type,
            AuditLog.resource_id == resource_id
        )\
        .order_by(AuditLog.created_at.desc())\
        .limit(limit)\
        .offset(offset)\
        .all()


def get_admin_audit_logs(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    action_filter: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[AuditLog]:
    """Get audit logs for admin actions"""
    query = db.query(AuditLog).filter(AuditLog.action.like("admin.%"))

    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)

    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)

    if action_filter:
        query = query.filter(AuditLog.action.like(f"%{action_filter}%"))

    return query.order_by(AuditLog.created_at.desc())\
        .limit(limit)\
        .offset(offset)\
        .all()


def cleanup_old_audit_logs(db: Session, days_to_keep: int = 365) -> int:
    """
    Clean up audit logs older than specified days
    Returns number of deleted records
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

    deleted = db.query(AuditLog)\
        .filter(AuditLog.created_at < cutoff_date)\
        .delete()

    db.commit()

    logger.info(f"Cleaned up {deleted} old audit log entries")
    return deleted