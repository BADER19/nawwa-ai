"""Initial schema with proper constraints and indexes

Revision ID: 001
Revises:
Create Date: 2025-11-02 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create SubscriptionTier enum
    subscription_tier_enum = postgresql.ENUM('free', 'pro', 'team', 'enterprise', name='subscriptiontier')
    subscription_tier_enum.create(op.get_bind(), checkfirst=True)

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('subscription_tier', subscription_tier_enum, nullable=False),
        sa.Column('stripe_customer_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True),
        sa.Column('subscription_status', sa.String(length=50), nullable=False),
        sa.Column('usage_count', sa.Integer(), nullable=False),
        sa.Column('usage_reset_date', sa.DateTime(), nullable=False),
        sa.Column('trial_ends_at', sa.DateTime(), nullable=True),
        sa.CheckConstraint('usage_count >= 0', name='check_usage_count_non_negative'),
        sa.CheckConstraint(
            "subscription_status IN ('active', 'canceled', 'past_due', 'trialing', 'incomplete', 'incomplete_expired', 'unpaid')",
            name='check_valid_subscription_status'
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('stripe_customer_id'),
        sa.UniqueConstraint('stripe_subscription_id')
    )
    op.create_index('idx_user_created_at', 'users', ['created_at'])
    op.create_index('idx_user_tier_status', 'users', ['subscription_tier', 'subscription_status'])
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_stripe_customer_id'), 'users', ['stripe_customer_id'], unique=False)
    op.create_index(op.f('ix_users_stripe_subscription_id'), 'users', ['stripe_subscription_id'], unique=False)

    # Create workspaces table
    op.create_table(
        'workspaces',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_workspace_owner_created', 'workspaces', ['owner_id', 'created_at'])
    op.create_index('idx_workspace_owner_updated', 'workspaces', ['owner_id', 'updated_at'])
    op.create_index(op.f('ix_workspaces_id'), 'workspaces', ['id'], unique=False)
    op.create_index(op.f('ix_workspaces_owner_id'), 'workspaces', ['owner_id'], unique=False)

    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('user_role', sa.String(length=100), nullable=False),
        sa.Column('audience', sa.String(length=100), nullable=False),
        sa.Column('goal', sa.String(length=100), nullable=False),
        sa.Column('setting', sa.String(length=100), nullable=False),
        sa.Column('tone', sa.String(length=50), nullable=True),
        sa.Column('depth', sa.String(length=50), nullable=True),
        sa.Column('context_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('topics', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_project_owner_created', 'projects', ['owner_id', 'created_at'])
    op.create_index('idx_project_owner_updated', 'projects', ['owner_id', 'updated_at'])
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)
    op.create_index(op.f('ix_projects_owner_id'), 'projects', ['owner_id'], unique=False)

    # Create project_visualizations table
    op.create_table(
        'project_visualizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('slide_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('speaker_notes', sa.Text(), nullable=True),
        sa.Column('annotations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint('slide_number >= 1', name='check_slide_number_positive'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id', 'slide_number', name='uq_project_slide_number')
    )
    op.create_index('idx_project_viz_project_slide', 'project_visualizations', ['project_id', 'slide_number'])
    op.create_index(op.f('ix_project_visualizations_id'), 'project_visualizations', ['id'], unique=False)
    op.create_index(op.f('ix_project_visualizations_project_id'), 'project_visualizations', ['project_id'], unique=False)


def downgrade() -> None:
    # Drop all tables in reverse order
    op.drop_index(op.f('ix_project_visualizations_project_id'), table_name='project_visualizations')
    op.drop_index(op.f('ix_project_visualizations_id'), table_name='project_visualizations')
    op.drop_index('idx_project_viz_project_slide', table_name='project_visualizations')
    op.drop_table('project_visualizations')

    op.drop_index(op.f('ix_projects_owner_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_id'), table_name='projects')
    op.drop_index('idx_project_owner_updated', table_name='projects')
    op.drop_index('idx_project_owner_created', table_name='projects')
    op.drop_table('projects')

    op.drop_index(op.f('ix_workspaces_owner_id'), table_name='workspaces')
    op.drop_index(op.f('ix_workspaces_id'), table_name='workspaces')
    op.drop_index('idx_workspace_owner_updated', table_name='workspaces')
    op.drop_index('idx_workspace_owner_created', table_name='workspaces')
    op.drop_table('workspaces')

    op.drop_index(op.f('ix_users_stripe_subscription_id'), table_name='users')
    op.drop_index(op.f('ix_users_stripe_customer_id'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index('idx_user_tier_status', table_name='users')
    op.drop_index('idx_user_created_at', table_name='users')
    op.drop_table('users')

    # Drop enum
    subscription_tier_enum = postgresql.ENUM('free', 'pro', 'team', 'enterprise', name='subscriptiontier')
    subscription_tier_enum.drop(op.get_bind(), checkfirst=True)
