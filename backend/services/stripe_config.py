import os
import stripe

# Initialize Stripe with API key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Stripe product price IDs (you'll create these in Stripe Dashboard)
STRIPE_PRICE_IDS = {
    "pro_monthly": os.getenv("STRIPE_PRO_MONTHLY_PRICE_ID", "price_pro_monthly"),
    "pro_yearly": os.getenv("STRIPE_PRO_YEARLY_PRICE_ID", "price_pro_yearly"),
    "team_monthly": os.getenv("STRIPE_TEAM_MONTHLY_PRICE_ID", "price_team_monthly"),
    "team_yearly": os.getenv("STRIPE_TEAM_YEARLY_PRICE_ID", "price_team_yearly"),
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

# Webhook secret
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
