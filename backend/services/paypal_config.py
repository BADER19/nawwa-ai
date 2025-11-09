import os
import paypalrestsdk

# Initialize PayPal with credentials
paypalrestsdk.configure({
    "mode": os.getenv("PAYPAL_MODE", "sandbox"),  # sandbox or live
    "client_id": os.getenv("PAYPAL_CLIENT_ID"),
    "client_secret": os.getenv("PAYPAL_CLIENT_SECRET")
})

# PayPal subscription plan IDs (you'll create these in PayPal Dashboard)
PAYPAL_PLAN_IDS = {
    "pro_monthly": os.getenv("PAYPAL_PRO_MONTHLY_PLAN_ID", "P-XXXXXXXXXXXXXXXXXXXX"),
    "pro_yearly": os.getenv("PAYPAL_PRO_YEARLY_PLAN_ID", "P-XXXXXXXXXXXXXXXXXXXX"),
    "team_monthly": os.getenv("PAYPAL_TEAM_MONTHLY_PLAN_ID", "P-XXXXXXXXXXXXXXXXXXXX"),
    "team_yearly": os.getenv("PAYPAL_TEAM_YEARLY_PLAN_ID", "P-XXXXXXXXXXXXXXXXXXXX"),
}

# Tier limits (keys are uppercase to match database enum values)
TIER_LIMITS = {
    "FREE": {
        "ai_requests_per_day": 20,  # 20 AI visualizations per day
        "workspaces": 3,
        "features": ["basic_shapes", "ai_visualization", "community_support"]
    },
    "PRO": {
        "ai_requests_per_day": -1,  # Unlimited AI requests
        "workspaces": -1,  # -1 = unlimited
        "features": ["all_visualizations", "unlimited_ai", "celebrity_images", "exports", "priority_support"]
    },
    "TEAM": {
        "ai_requests_per_day": -1,  # Unlimited
        "workspaces": -1,
        "team_members": 5,
        "features": ["all_visualizations", "unlimited_ai", "celebrity_images", "exports", "team_collaboration", "api_access", "custom_branding", "priority_chat"]
    },
    "ENTERPRISE": {
        "ai_requests_per_day": -1,  # Unlimited
        "workspaces": -1,
        "team_members": -1,
        "features": ["everything", "on_premise", "dedicated_infrastructure", "white_label", "sla", "account_manager"]
    }
}

# Webhook ID for verifying PayPal webhooks
PAYPAL_WEBHOOK_ID = os.getenv("PAYPAL_WEBHOOK_ID", "")
