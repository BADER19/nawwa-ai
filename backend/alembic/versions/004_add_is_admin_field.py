"""Add is_admin field to users

Revision ID: 004
Revises: 003
Create Date: 2025-01-09

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Add is_admin column to users table
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'))

    # Create index on is_admin for faster admin queries
    op.create_index('ix_users_is_admin', 'users', ['is_admin'])


def downgrade():
    # Remove index
    op.drop_index('ix_users_is_admin', table_name='users')

    # Remove is_admin column
    op.drop_column('users', 'is_admin')
