import paypalrestsdk
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import logging

from models.user import User, SubscriptionTier
from services.paypal_config import PAYPAL_PLAN_IDS, TIER_LIMITS

logger = logging.getLogger("subscription_service")


def check_usage_limit(user: User, db: Session) -> tuple[bool, str]:
    """
    Check if user has exceeded their usage limit.
    Returns (can_use, error_message)

    WARNING: This function may modify user.usage_count and user.usage_reset_date
    The caller MUST ensure these changes are persisted via db.commit()
    """
    tier = user.subscription_tier.value
    limits = TIER_LIMITS.get(tier, TIER_LIMITS["FREE"])

    # Reset usage if period has expired (daily reset)
    if datetime.utcnow() >= user.usage_reset_date:
        user.usage_count = 0
        user.usage_reset_date = datetime.utcnow() + timedelta(days=1)
        logger.info(f"Reset daily quota for user {user.email}")
        # Note: Changes will be committed by caller

    # Check limits (daily AI requests)
    max_ai_requests = limits.get("ai_requests_per_day", 20)

    if max_ai_requests == -1:  # Unlimited
        return True, ""

    if user.usage_count >= max_ai_requests:
        hours_until_reset = max(1, int((user.usage_reset_date - datetime.utcnow()).total_seconds() / 3600))
        return False, f"Daily AI quota exceeded. You've used {user.usage_count}/{max_ai_requests} AI requests today. Resets in {hours_until_reset}h. Upgrade for unlimited access."

    return True, ""


def increment_usage(user: User, db: Session):
    """
    Increment user's usage count
    Note: The caller should handle db.commit() to ensure atomicity with other operations
    """
    user.usage_count += 1
    logger.info(f"User {user.email} usage: {user.usage_count}")


def create_subscription(
    user: User,
    plan_id: str,
    success_url: str,
    cancel_url: str
) -> Dict[str, Any]:
    """
    Create a PayPal Subscription for a plan
    """
    try:
        # Create billing agreement (subscription)
        billing_agreement = paypalrestsdk.BillingAgreement({
            "name": "Nawwa Subscription",
            "description": "Subscription to Nawwa visualization service",
            "start_date": (datetime.utcnow() + timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "plan": {
                "id": plan_id
            },
            "payer": {
                "payment_method": "paypal",
                "payer_info": {
                    "email": user.email
                }
            }
        })

        if billing_agreement.create():
            # Get approval URL
            for link in billing_agreement.links:
                if link.rel == "approval_url":
                    approval_url = link.href
                    logger.info(f"Created subscription for user {user.email}: {billing_agreement.id}")
                    return {
                        "subscription_id": billing_agreement.id,
                        "approval_url": approval_url
                    }
            raise ValueError("No approval URL found in response")
        else:
            logger.error(f"Failed to create subscription: {billing_agreement.error}")
            raise ValueError(f"PayPal error: {billing_agreement.error}")

    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        raise


def execute_subscription(agreement_token: str, user: User, db: Session) -> Dict[str, Any]:
    """
    Execute (activate) a PayPal subscription after user approval
    """
    try:
        billing_agreement = paypalrestsdk.BillingAgreement.execute(agreement_token)

        if billing_agreement:
            # Save subscription details
            user.paypal_subscription_id = billing_agreement.id
            user.paypal_payer_id = billing_agreement.payer.payer_info.payer_id
            user.subscription_status = billing_agreement.state.lower()  # active, suspended, cancelled

            # Determine tier from plan
            plan_id = billing_agreement.plan.id
            user.subscription_tier = get_tier_from_plan_id(plan_id)

            # Reset usage
            user.usage_count = 0
            user.usage_reset_date = datetime.utcnow() + timedelta(days=1)

            db.commit()
            logger.info(f"Executed subscription for user {user.email}: {billing_agreement.id}")

            return {
                "subscription_id": billing_agreement.id,
                "status": billing_agreement.state,
                "tier": user.subscription_tier.value
            }
        else:
            raise ValueError("Failed to execute billing agreement")

    except Exception as e:
        db.rollback()
        logger.error(f"Error executing subscription: {str(e)}")
        raise


def cancel_subscription(user: User, db: Session) -> Dict[str, Any]:
    """
    Cancel user's PayPal subscription
    """
    try:
        if not user.paypal_subscription_id:
            raise ValueError("User has no active subscription")

        billing_agreement = paypalrestsdk.BillingAgreement.find(user.paypal_subscription_id)

        if billing_agreement.cancel({"note": "User requested cancellation"}):
            user.subscription_status = "cancelled"
            user.subscription_tier = SubscriptionTier.FREE
            user.paypal_subscription_id = None
            user.usage_count = 0
            user.usage_reset_date = datetime.utcnow() + timedelta(days=1)

            db.commit()
            logger.info(f"Cancelled subscription for user {user.email}")

            return {"status": "cancelled"}
        else:
            raise ValueError("Failed to cancel subscription")

    except Exception as e:
        db.rollback()
        logger.error(f"Error cancelling subscription: {str(e)}")
        raise


def handle_subscription_created(subscription_data: Dict[str, Any], db: Session):
    """
    Handle subscription created webhook from PayPal
    """
    try:
        subscription_id = subscription_data.get("id")
        payer_email = subscription_data.get("subscriber", {}).get("email_address")
        plan_id = subscription_data.get("plan_id")
        status = subscription_data.get("status", "").lower()

        # Find user by email
        user = db.query(User).filter(User.email == payer_email).first()
        if not user:
            logger.error(f"User not found for email {payer_email}")
            return

        # Update user subscription
        user.paypal_subscription_id = subscription_id
        user.subscription_tier = get_tier_from_plan_id(plan_id)
        user.subscription_status = status
        user.usage_count = 0
        user.usage_reset_date = datetime.utcnow() + timedelta(days=1)

        db.commit()
        logger.info(f"Subscription created for user {user.email}: {user.subscription_tier.value}")

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to handle subscription created: {str(e)}")
        raise


def handle_subscription_updated(subscription_data: Dict[str, Any], db: Session):
    """
    Handle subscription updated webhook from PayPal
    """
    try:
        subscription_id = subscription_data.get("id")
        status = subscription_data.get("status", "").lower()

        user = db.query(User).filter(User.paypal_subscription_id == subscription_id).first()
        if not user:
            logger.error(f"User not found for subscription {subscription_id}")
            return

        user.subscription_status = status

        # If subscription suspended or cancelled, downgrade to free
        if status in ["suspended", "cancelled"]:
            user.subscription_tier = SubscriptionTier.FREE

        db.commit()
        logger.info(f"Subscription updated for user {user.email}: {status}")

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to handle subscription updated: {str(e)}")
        raise


def handle_subscription_cancelled(subscription_data: Dict[str, Any], db: Session):
    """
    Handle subscription cancelled webhook from PayPal
    """
    try:
        subscription_id = subscription_data.get("id")

        user = db.query(User).filter(User.paypal_subscription_id == subscription_id).first()
        if not user:
            logger.error(f"User not found for subscription {subscription_id}")
            return

        user.subscription_tier = SubscriptionTier.FREE
        user.subscription_status = "cancelled"
        user.paypal_subscription_id = None
        user.usage_count = 0
        user.usage_reset_date = datetime.utcnow() + timedelta(days=1)

        db.commit()
        logger.info(f"Subscription cancelled for user {user.email}")

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to handle subscription cancelled: {str(e)}")
        raise


def handle_payment_failed(payment_data: Dict[str, Any], db: Session):
    """
    Handle payment failure webhook from PayPal
    """
    try:
        subscription_id = payment_data.get("billing_agreement_id")

        user = db.query(User).filter(User.paypal_subscription_id == subscription_id).first()
        if not user:
            logger.error(f"User not found for subscription {subscription_id}")
            return

        user.subscription_status = "past_due"
        db.commit()
        logger.warning(f"Payment failed for user {user.email}")

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to handle payment failure: {str(e)}")
        raise


def get_tier_from_plan_id(plan_id: str) -> SubscriptionTier:
    """Map PayPal plan ID to subscription tier"""
    if plan_id in [PAYPAL_PLAN_IDS["pro_monthly"], PAYPAL_PLAN_IDS["pro_yearly"]]:
        return SubscriptionTier.PRO
    elif plan_id in [PAYPAL_PLAN_IDS["team_monthly"], PAYPAL_PLAN_IDS["team_yearly"]]:
        return SubscriptionTier.TEAM
    else:
        return SubscriptionTier.FREE


def get_user_subscription_info(user: User) -> Dict[str, Any]:
    """Get formatted subscription info for user"""
    tier = user.subscription_tier.value
    limits = TIER_LIMITS.get(tier, TIER_LIMITS["FREE"])

    # Calculate usage percentage (daily AI requests)
    max_ai_requests = limits.get("ai_requests_per_day", 20)
    usage_percentage = 0
    if max_ai_requests > 0:
        usage_percentage = (user.usage_count / max_ai_requests) * 100

    return {
        "tier": tier,
        "status": user.subscription_status,
        "usage_count": user.usage_count,
        "usage_limit": max_ai_requests if max_ai_requests > 0 else "unlimited",
        "usage_percentage": usage_percentage,
        "usage_reset_date": user.usage_reset_date.isoformat(),
        "features": limits.get("features", []),
        "has_paypal_subscription": bool(user.paypal_subscription_id),
    }
