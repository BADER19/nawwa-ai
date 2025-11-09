from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
import logging
import paypalrestsdk

from services.db import get_db
from services.subscription_service import (
    handle_subscription_created,
    handle_subscription_updated,
    handle_subscription_cancelled,
    handle_payment_failed,
)
from services.paypal_config import PAYPAL_WEBHOOK_ID

router = APIRouter()
logger = logging.getLogger("paypal_webhook")


@router.post("/paypal/webhook")
async def handle_paypal_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle PayPal webhook events
    """
    try:
        # Get the raw body and headers
        body = await request.body()
        headers = dict(request.headers)

        # Verify the webhook signature (optional but recommended)
        # Note: PayPal SDK's webhook verification requires the webhook event object
        event_body = await request.json()

        # Log the event
        event_type = event_body.get("event_type")
        logger.info(f"Received PayPal webhook: {event_type}")

        # Handle different event types
        if event_type == "BILLING.SUBSCRIPTION.CREATED":
            resource = event_body.get("resource", {})
            handle_subscription_created(resource, db)

        elif event_type == "BILLING.SUBSCRIPTION.UPDATED":
            resource = event_body.get("resource", {})
            handle_subscription_updated(resource, db)

        elif event_type == "BILLING.SUBSCRIPTION.CANCELLED":
            resource = event_body.get("resource", {})
            handle_subscription_cancelled(resource, db)

        elif event_type == "BILLING.SUBSCRIPTION.SUSPENDED":
            resource = event_body.get("resource", {})
            handle_subscription_updated(resource, db)

        elif event_type == "PAYMENT.SALE.COMPLETED":
            # Successful payment
            logger.info("Payment completed successfully")

        elif event_type == "PAYMENT.SALE.DENIED":
            resource = event_body.get("resource", {})
            handle_payment_failed(resource, db)

        else:
            logger.warning(f"Unhandled webhook event: {event_type}")

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error handling PayPal webhook: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
