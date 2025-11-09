"""Add subscription fields to users table

Revision ID: 002
Revises: 001
Create Date: 2025-11-02 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to users table
    # Use text() with cast for enum default value - note: enum values are UPPERCASE
    op.add_column('users', sa.Column('subscription_tier', postgresql.ENUM('FREE', 'PRO', 'TEAM', 'ENTERPRISE', name='subscriptiontier', create_type=False), nullable=False, server_default=sa.text("'FREE'::subscriptiontier")))
    op.add_column('users', sa.Column('stripe_customer_id', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('subscription_status', sa.String(length=50), nullable=False, server_default='active'))
    op.add_column('users', sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('usage_reset_date', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')))
    op.add_column('users', sa.Column('trial_ends_at', sa.DateTime(), nullable=True))

    # Create unique constraints
    op.create_unique_constraint('uq_users_stripe_customer_id', 'users', ['stripe_customer_id'])
    op.create_unique_constraint('uq_users_stripe_subscription_id', 'users', ['stripe_subscription_id'])

    # Create check constraints
    op.create_check_constraint('check_usage_count_non_negative', 'users', 'usage_count >= 0')
    op.create_check_constraint(
        'check_valid_subscription_status',
        'users',
        "subscription_status IN ('active', 'canceled', 'past_due', 'trialing', 'incomplete', 'incomplete_expired', 'unpaid')"
    )

    # Create indexes
    op.create_index('ix_users_stripe_customer_id', 'users', ['stripe_customer_id'], unique=False)
    op.create_index('ix_users_stripe_subscription_id', 'users', ['stripe_subscription_id'], unique=False)
    op.create_index('idx_user_created_at', 'users', ['created_at'], unique=False)
    op.create_index('idx_user_tier_status', 'users', ['subscription_tier', 'subscription_status'], unique=False)

    # Create indexes for workspaces
    op.create_index('idx_workspace_owner_created', 'workspaces', ['owner_id', 'created_at'], unique=False)
    op.create_index('idx_workspace_owner_updated', 'workspaces', ['owner_id', 'updated_at'], unique=False)

    # Create indexes for projects
    op.create_index('idx_project_owner_created', 'projects', ['owner_id', 'created_at'], unique=False)
    op.create_index('idx_project_owner_updated', 'projects', ['owner_id', 'updated_at'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_project_owner_updated', table_name='projects')
    op.drop_index('idx_project_owner_created', table_name='projects')
    op.drop_index('idx_workspace_owner_updated', table_name='workspaces')
    op.drop_index('idx_workspace_owner_created', table_name='workspaces')
    op.drop_index('idx_user_tier_status', table_name='users')
    op.drop_index('idx_user_created_at', table_name='users')
    op.drop_index('ix_users_stripe_subscription_id', table_name='users')
    op.drop_index('ix_users_stripe_customer_id', table_name='users')

    # Drop constraints
    op.drop_constraint('check_valid_subscription_status', 'users', type_='check')
    op.drop_constraint('check_usage_count_non_negative', 'users', type_='check')
    op.drop_constraint('uq_users_stripe_subscription_id', 'users', type_='unique')
    op.drop_constraint('uq_users_stripe_customer_id', 'users', type_='unique')

    # Drop columns
    op.drop_column('users', 'trial_ends_at')
    op.drop_column('users', 'usage_reset_date')
    op.drop_column('users', 'usage_count')
    op.drop_column('users', 'subscription_status')
    op.drop_column('users', 'stripe_subscription_id')
    op.drop_column('users', 'stripe_customer_id')
    op.drop_column('users', 'subscription_tier')
