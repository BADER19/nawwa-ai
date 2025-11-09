#!/usr/bin/env python
"""
Script to create PayPal subscription plans.
Run this to set up your subscription plans in PayPal.
"""

import os
import sys
import json
import paypalrestsdk
from dotenv import load_dotenv

# Load environment variables
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
env_path = os.path.join(base_dir, "infra", ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)

# Configure PayPal SDK
paypalrestsdk.configure({
    "mode": os.getenv("PAYPAL_MODE", "sandbox"),
    "client_id": os.getenv("PAYPAL_CLIENT_ID"),
    "client_secret": os.getenv("PAYPAL_CLIENT_SECRET")
})

# Plan configurations
PLANS = [
    {
        "name": "Nawwa Pro Monthly",
        "description": "Professional visualization tools - Monthly subscription",
        "price": "19.00",
        "interval": "MONTH",
        "env_key": "PAYPAL_PRO_MONTHLY_PLAN_ID"
    },
    {
        "name": "Nawwa Pro Yearly",
        "description": "Professional visualization tools - Annual subscription (save $38/year)",
        "price": "190.00",
        "interval": "YEAR",
        "env_key": "PAYPAL_PRO_YEARLY_PLAN_ID"
    },
    {
        "name": "Nawwa Team Monthly",
        "description": "Team collaboration and advanced features - Monthly subscription",
        "price": "49.00",
        "interval": "MONTH",
        "env_key": "PAYPAL_TEAM_MONTHLY_PLAN_ID"
    },
    {
        "name": "Nawwa Team Yearly",
        "description": "Team collaboration and advanced features - Annual subscription (save $98/year)",
        "price": "490.00",
        "interval": "YEAR",
        "env_key": "PAYPAL_TEAM_YEARLY_PLAN_ID"
    }
]

def create_plan(plan_config):
    """Create a subscription plan in PayPal."""
    billing_plan = paypalrestsdk.BillingPlan({
        "name": plan_config["name"],
        "description": plan_config["description"],
        "type": "INFINITE",
        "payment_definitions": [{
            "name": "Regular payment",
            "type": "REGULAR",
            "frequency": plan_config["interval"],
            "frequency_interval": "1",
            "amount": {
                "value": plan_config["price"],
                "currency": "USD"
            },
            "cycles": "0"
        }],
        "merchant_preferences": {
            "return_url": "https://nawwa.ai/subscription/success",
            "cancel_url": "https://nawwa.ai/subscription/cancel",
            "auto_bill_amount": "YES",
            "initial_fail_amount_action": "CONTINUE",
            "max_fail_attempts": "3"
        }
    })

    if billing_plan.create():
        print(f"✅ Created plan: {plan_config['name']}")
        print(f"   Plan ID: {billing_plan.id}")

        # Activate the plan
        if billing_plan.activate():
            print(f"   Status: ACTIVATED")
        else:
            print(f"   ⚠️ Failed to activate: {billing_plan.error}")

        return billing_plan.id
    else:
        print(f"❌ Failed to create plan: {plan_config['name']}")
        print(f"   Error: {billing_plan.error}")
        return None

def main():
    """Main function to create all plans."""
    print("🚀 PayPal Subscription Plan Setup")
    print("="*50)

    # Check credentials
    if not os.getenv("PAYPAL_CLIENT_ID") or not os.getenv("PAYPAL_CLIENT_SECRET"):
        print("❌ Missing PayPal credentials in environment variables!")
        print("   Please set PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET")
        sys.exit(1)

    print(f"Mode: {os.getenv('PAYPAL_MODE', 'sandbox')}")
    print(f"Client ID: {os.getenv('PAYPAL_CLIENT_ID')[:20]}...")
    print()

    # Create plans
    created_plans = {}
    for plan in PLANS:
        print(f"Creating {plan['name']}...")
        plan_id = create_plan(plan)
        if plan_id:
            created_plans[plan["env_key"]] = plan_id
        print()

    # Output environment variables
    if created_plans:
        print("\n" + "="*50)
        print("✅ Plans created successfully!")
        print("\n📝 Add these to your .env file:")
        print("-"*50)
        for key, value in created_plans.items():
            print(f"{key}={value}")
        print("-"*50)

        # Also save to a file
        output_file = "paypal_plan_ids.txt"
        with open(output_file, "w") as f:
            f.write("# PayPal Subscription Plan IDs\n")
            f.write(f"# Generated on: {os.popen('date').read()}\n")
            f.write("#\n")
            f.write("# Add these to your infra/.env file:\n\n")
            for key, value in created_plans.items():
                f.write(f"{key}={value}\n")

        print(f"\n📄 Plan IDs also saved to: {output_file}")
    else:
        print("\n❌ No plans were created successfully.")
        print("   Please check your PayPal credentials and try again.")

if __name__ == "__main__":
    main()