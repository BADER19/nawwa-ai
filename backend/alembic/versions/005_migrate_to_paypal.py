"""Migrate from Stripe to PayPal

Revision ID: 005
Revises: 004
Create Date: 2024-11-09 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    # Drop old Stripe columns
    op.drop_column('users', 'stripe_customer_id')
    op.drop_column('users', 'stripe_subscription_id')

    # Add new PayPal columns
    op.add_column('users', sa.Column('paypal_subscription_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('paypal_payer_id', sa.String(255), nullable=True))

    # Create unique index on paypal_subscription_id
    op.create_index('ix_users_paypal_subscription_id', 'users', ['paypal_subscription_id'], unique=True)
    op.create_index('ix_users_paypal_payer_id', 'users', ['paypal_payer_id'], unique=False)

    # Update subscription status constraint
    op.drop_constraint('check_valid_subscription_status', 'users', type_='check')
    op.create_check_constraint(
        'check_valid_subscription_status',
        'users',
        "subscription_status IN ('active', 'cancelled', 'suspended', 'past_due', 'pending', 'expired')"
    )


def downgrade():
    # Remove PayPal columns
    op.drop_index('ix_users_paypal_subscription_id', 'users')
    op.drop_index('ix_users_paypal_payer_id', 'users')
    op.drop_column('users', 'paypal_subscription_id')
    op.drop_column('users', 'paypal_payer_id')

    # Restore Stripe columns
    op.add_column('users', sa.Column('stripe_customer_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('stripe_subscription_id', sa.String(255), nullable=True))

    # Recreate unique indexes
    op.create_index('ix_users_stripe_customer_id', 'users', ['stripe_customer_id'], unique=True)
    op.create_index('ix_users_stripe_subscription_id', 'users', ['stripe_subscription_id'], unique=True)

    # Restore old constraint
    op.drop_constraint('check_valid_subscription_status', 'users', type_='check')
    op.create_check_constraint(
        'check_valid_subscription_status',
        'users',
        "subscription_status IN ('active', 'canceled', 'past_due', 'trialing', 'incomplete', 'incomplete_expired', 'unpaid')"
    )