from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Dict, List, Any
from services.db import get_db
from models.user import User
from utils.auth_deps import get_admin_user

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive dashboard statistics.
    Requires admin access.
    """

    # Get total users
    total_users = db.query(func.count(User.id)).scalar()

    # Get users by tier
    tier_stats = db.query(
        User.subscription_tier,
        func.count(User.id)
    ).group_by(User.subscription_tier).all()

    # Get recent signups (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_signups = db.query(func.count(User.id)).filter(
        User.created_at > seven_days_ago
    ).scalar()

    # Get today's signups
    today = datetime.utcnow().date()
    today_signups = db.query(func.count(User.id)).filter(
        func.date(User.created_at) == today
    ).scalar()

    # Get admin count
    admin_count = db.query(func.count(User.id)).filter(
        User.is_admin == True
    ).scalar()

    # Get total usage
    total_usage = db.query(func.sum(User.usage_count)).scalar() or 0
    avg_usage = total_usage / total_users if total_users > 0 else 0

    # Get recent users
    recent_users = db.query(User).order_by(
        User.created_at.desc()
    ).limit(10).all()

    # Get most active users
    active_users = db.query(User).filter(
        User.usage_count > 0
    ).order_by(User.usage_count.desc()).limit(10).all()

    # Calculate growth rate
    fourteen_days_ago = datetime.utcnow() - timedelta(days=14)
    last_week_signups = db.query(func.count(User.id)).filter(
        User.created_at > fourteen_days_ago,
        User.created_at <= seven_days_ago
    ).scalar()

    growth_rate = 0
    if last_week_signups > 0:
        growth_rate = ((recent_signups - last_week_signups) / last_week_signups) * 100

    return {
        "summary": {
            "total_users": total_users,
            "admin_count": admin_count,
            "today_signups": today_signups,
            "week_signups": recent_signups,
            "total_usage": total_usage,
            "avg_usage_per_user": round(avg_usage, 1),
            "growth_rate_percent": round(growth_rate, 1)
        },
        "tier_breakdown": {
            tier: count for tier, count in tier_stats
        },
        "recent_users": [
            {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "tier": user.subscription_tier.value,
                "is_admin": user.is_admin,
                "usage": user.usage_count,
                "joined": user.created_at.isoformat(),
                "days_ago": (datetime.utcnow() - user.created_at).days
            }
            for user in recent_users
        ],
        "most_active_users": [
            {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "tier": user.subscription_tier.value,
                "usage": user.usage_count
            }
            for user in active_users
        ],
        "generated_at": datetime.utcnow().isoformat()
    }

@router.get("/users/export")
async def export_users_csv(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> str:
    """
    Export all users as CSV format.
    Requires admin access.
    You can copy this to Excel.
    """

    users = db.query(User).order_by(User.id).all()

    # Create CSV header
    csv_lines = ["ID,Email,Username,Tier,Admin,Usage,Created"]

    # Add user rows
    for user in users:
        csv_lines.append(
            f"{user.id},"
            f"{user.email},"
            f"{user.username or ''},"
            f"{user.subscription_tier.value},"
            f"{user.is_admin},"
            f"{user.usage_count},"
            f"{user.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    return "\n".join(csv_lines)

@router.get("/users/table")
async def get_users_table(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get all users in table format for easy viewing.
    Requires admin access.
    """

    users = db.query(User).order_by(User.created_at.desc()).all()

    return {
        "total": len(users),
        "users": [
            {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "tier": user.subscription_tier.value,
                "is_admin": user.is_admin,
                "usage_count": user.usage_count,
                "created_at": user.created_at.isoformat(),
                "days_since_joined": (datetime.utcnow() - user.created_at).days
            }
            for user in users
        ]
    }