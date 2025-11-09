from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from utils.auth_deps import get_current_user
from services.db import get_db
from models.user import User
from services.subscription_service import (
    create_subscription,
    execute_subscription,
    cancel_subscription,
    get_user_subscription_info,
)
from services.paypal_config import PAYPAL_PLAN_IDS

router = APIRouter()


class CheckoutRequest(BaseModel):
    plan: str  # "pro_monthly", "pro_yearly", "team_monthly", "team_yearly"
    success_url: str
    cancel_url: str


class ExecuteSubscriptionRequest(BaseModel):
    token: str  # PayPal agreement token from redirect


class CancelSubscriptionRequest(BaseModel):
    reason: Optional[str] = None


@router.post("/create-checkout-session")
def create_checkout(
    req: CheckoutRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a PayPal Subscription for a plan
    """
    plan_id = PAYPAL_PLAN_IDS.get(req.plan)
    if not plan_id:
        raise HTTPException(status_code=400, detail="Invalid plan")

    try:
        subscription_data = create_subscription(
            user=user,
            plan_id=plan_id,
            success_url=req.success_url,
            cancel_url=req.cancel_url
        )

        # Return approval URL for PayPal checkout
        return {
            "url": subscription_data["approval_url"],
            "subscription_id": subscription_data["subscription_id"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute-subscription")
def execute_agreement(
    req: ExecuteSubscriptionRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Execute (activate) a PayPal subscription after user approves
    """
    try:
        result = execute_subscription(
            agreement_token=req.token,
            user=user,
            db=db
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cancel-subscription")
def cancel_user_subscription(
    req: CancelSubscriptionRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel user's PayPal subscription
    """
    try:
        result = cancel_subscription(user=user, db=db)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subscription-info")
def get_subscription_info(user: User = Depends(get_current_user)):
    """
    Get current user's subscription information
    """
    return get_user_subscription_info(user)


@router.get("/plans")
def get_available_plans():
    """
    Get available subscription plans with pricing
    """
    return {
        "plans": [
            {
                "id": "free",
                "name": "Free",
                "price": 0,
                "interval": "month",
                "features": [
                    "50 visualizations/month",
                    "Basic shapes & charts",
                    "3 saved workspaces",
                    "Community support"
                ]
            },
            {
                "id": "pro_monthly",
                "name": "Pro",
                "price": 19,
                "interval": "month",
                "paypal_plan_id": PAYPAL_PLAN_IDS["pro_monthly"],
                "features": [
                    "500 visualizations/month",
                    "All visualization types",
                    "Unlimited workspaces",
                    "Celebrity images & exports",
                    "Priority email support"
                ]
            },
            {
                "id": "pro_yearly",
                "name": "Pro (Annual)",
                "price": 190,
                "interval": "year",
                "monthly_equivalent": 15.83,
                "savings": 38,
                "paypal_plan_id": PAYPAL_PLAN_IDS["pro_yearly"],
                "features": [
                    "500 visualizations/month",
                    "All visualization types",
                    "Unlimited workspaces",
                    "Celebrity images & exports",
                    "Priority email support",
                    "Save $38/year"
                ]
            },
            {
                "id": "team_monthly",
                "name": "Team",
                "price": 49,
                "interval": "month",
                "paypal_plan_id": PAYPAL_PLAN_IDS["team_monthly"],
                "features": [
                    "2,500 visualizations/month",
                    "Up to 5 team members",
                    "Team collaboration",
                    "API access (10K calls/mo)",
                    "Custom branding",
                    "Priority chat support"
                ]
            },
            {
                "id": "team_yearly",
                "name": "Team (Annual)",
                "price": 490,
                "interval": "year",
                "monthly_equivalent": 40.83,
                "savings": 98,
                "paypal_plan_id": PAYPAL_PLAN_IDS["team_yearly"],
                "features": [
                    "2,500 visualizations/month",
                    "Up to 5 team members",
                    "Team collaboration",
                    "API access (10K calls/mo)",
                    "Custom branding",
                    "Priority chat support",
                    "Save $98/year"
                ]
            }
        ]
    }
