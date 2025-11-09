import stripe
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
import logging

from services.db import get_db
from services.stripe_config import STRIPE_WEBHOOK_SECRET
from services.subscription_service import (
    handle_subscription_created,
    handle_subscription_updated,
    handle_subscription_deleted,
    handle_payment_failed,
)

logger = logging.getLogger("stripe_webhook")
router = APIRouter()


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Stripe webhooks for subscription events
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")

    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    event_type = event["type"]
    data = event["data"]["object"]

    logger.info(f"Received webhook: {event_type}")

    try:
        if event_type == "customer.subscription.created":
            handle_subscription_created(data, db)

        elif event_type == "customer.subscription.updated":
            handle_subscription_updated(data, db)

        elif event_type == "customer.subscription.deleted":
            handle_subscription_deleted(data, db)

        elif event_type == "invoice.payment_failed":
            handle_payment_failed(data, db)

        elif event_type == "checkout.session.completed":
            # Session completed - subscription will be created via subscription.created
            logger.info(f"Checkout completed for session {data['id']}")

        else:
            logger.info(f"Unhandled event type: {event_type}")

    except Exception as e:
        logger.error(f"Error handling webhook {event_type}: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing error")

    return {"status": "success"}
