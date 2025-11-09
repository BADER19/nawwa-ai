"""
Script to create Stripe products and prices for InstantViz
Run this once to set up your Stripe account with the correct products and pricing
"""
import os
import stripe
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../../infra/.env')

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def create_products_and_prices():
    """Create Stripe products and prices"""

    print("🚀 Setting up Stripe products for InstantViz...")
    print("=" * 60)

    # Create PRO product
    print("\n📦 Creating PRO product...")
    pro_product = stripe.Product.create(
        name="InstantViz PRO",
        description="Professional plan with 500 visualizations/month and unlimited workspaces",
        metadata={
            "tier": "PRO",
            "visualizations_per_month": "500",
            "workspaces": "unlimited"
        }
    )
    print(f"✅ PRO Product created: {pro_product.id}")

    # Create PRO Monthly Price
    print("\n💰 Creating PRO Monthly price ($19/month)...")
    pro_monthly = stripe.Price.create(
        product=pro_product.id,
        unit_amount=1900,  # $19.00 in cents
        currency="usd",
        recurring={"interval": "month"},
        metadata={"tier": "PRO", "billing": "monthly"}
    )
    print(f"✅ PRO Monthly price created: {pro_monthly.id}")

    # Create PRO Yearly Price
    print("\n💰 Creating PRO Yearly price ($190/year)...")
    pro_yearly = stripe.Price.create(
        product=pro_product.id,
        unit_amount=19000,  # $190.00 in cents
        currency="usd",
        recurring={"interval": "year"},
        metadata={"tier": "PRO", "billing": "yearly"}
    )
    print(f"✅ PRO Yearly price created: {pro_yearly.id}")

    # Create TEAM product
    print("\n📦 Creating TEAM product...")
    team_product = stripe.Product.create(
        name="InstantViz TEAM",
        description="Team plan with 2,500 visualizations/month, 5 team members, and API access",
        metadata={
            "tier": "TEAM",
            "visualizations_per_month": "2500",
            "team_members": "5",
            "workspaces": "unlimited"
        }
    )
    print(f"✅ TEAM Product created: {team_product.id}")

    # Create TEAM Monthly Price
    print("\n💰 Creating TEAM Monthly price ($49/month)...")
    team_monthly = stripe.Price.create(
        product=team_product.id,
        unit_amount=4900,  # $49.00 in cents
        currency="usd",
        recurring={"interval": "month"},
        metadata={"tier": "TEAM", "billing": "monthly"}
    )
    print(f"✅ TEAM Monthly price created: {team_monthly.id}")

    # Create TEAM Yearly Price
    print("\n💰 Creating TEAM Yearly price ($490/year)...")
    team_yearly = stripe.Price.create(
        product=team_product.id,
        unit_amount=49000,  # $490.00 in cents
        currency="usd",
        recurring={"interval": "year"},
        metadata={"tier": "TEAM", "billing": "yearly"}
    )
    print(f"✅ TEAM Yearly price created: {team_yearly.id}")

    # Print summary
    print("\n" + "=" * 60)
    print("✨ All products and prices created successfully!")
    print("=" * 60)
    print("\n📝 Add these to your infra/.env file:")
    print(f"\nSTRIPE_PRO_MONTHLY_PRICE_ID={pro_monthly.id}")
    print(f"STRIPE_PRO_YEARLY_PRICE_ID={pro_yearly.id}")
    print(f"STRIPE_TEAM_MONTHLY_PRICE_ID={team_monthly.id}")
    print(f"STRIPE_TEAM_YEARLY_PRICE_ID={team_yearly.id}")
    print("\n" + "=" * 60)

    return {
        "pro_monthly": pro_monthly.id,
        "pro_yearly": pro_yearly.id,
        "team_monthly": team_monthly.id,
        "team_yearly": team_yearly.id
    }

if __name__ == "__main__":
    try:
        price_ids = create_products_and_prices()
        print("\n🎉 Setup complete! Your Stripe account is ready for payments.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nMake sure:")
        print("1. Your STRIPE_SECRET_KEY is set correctly in infra/.env")
        print("2. You have internet connection")
        print("3. Your Stripe account is active")
