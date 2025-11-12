"""Add security features columns

Revision ID: b9dcdf06ad8b
Revises: 005
Create Date: 2025-11-12 10:49:53.417338

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b9dcdf06ad8b'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Import for checking table existence
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)

    # Email verification columns
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('verification_token', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('verification_sent_at', sa.DateTime(), nullable=True))

    # Password reset columns
    op.add_column('users', sa.Column('reset_token', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('reset_token_expires', sa.DateTime(), nullable=True))

    # 2FA columns
    op.add_column('users', sa.Column('totp_secret', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('two_factor_enabled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('backup_codes', sa.String(length=1000), nullable=True))

    # Create indexes for performance
    op.create_index('ix_users_verification_token', 'users', ['verification_token'], unique=True)
    op.create_index('ix_users_reset_token', 'users', ['reset_token'], unique=True)

    # Create audit_logs table only if it doesn't exist
    if 'audit_logs' not in inspector.get_table_names():
        op.create_table(
            'audit_logs',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('user_email', sa.String(length=255), nullable=False),
            sa.Column('user_role', sa.String(length=50), nullable=False),
            sa.Column('action', sa.String(length=100), nullable=False),
            sa.Column('resource_type', sa.String(length=50), nullable=False),
            sa.Column('resource_id', sa.String(length=100), nullable=True),
            sa.Column('method', sa.String(length=10), nullable=False),
            sa.Column('endpoint', sa.String(length=255), nullable=False),
            sa.Column('ip_address', sa.String(length=45), nullable=True),
            sa.Column('user_agent', sa.Text(), nullable=True),
            sa.Column('old_values', sa.JSON(), nullable=True),
            sa.Column('new_values', sa.JSON(), nullable=True),
            sa.Column('changes', sa.JSON(), nullable=True),
            sa.Column('status_code', sa.Integer(), nullable=False),
            sa.Column('error_message', sa.Text(), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
        )

        # Create indexes on audit_logs
        op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
        op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
        op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])


def downgrade() -> None:
    # Drop audit_logs table
    op.drop_index('ix_audit_logs_created_at', 'audit_logs')
    op.drop_index('ix_audit_logs_action', 'audit_logs')
    op.drop_index('ix_audit_logs_user_id', 'audit_logs')
    op.drop_table('audit_logs')

    # Drop indexes
    op.drop_index('ix_users_reset_token', 'users')
    op.drop_index('ix_users_verification_token', 'users')

    # Drop 2FA columns
    op.drop_column('users', 'backup_codes')
    op.drop_column('users', 'two_factor_enabled')
    op.drop_column('users', 'totp_secret')

    # Drop password reset columns
    op.drop_column('users', 'reset_token_expires')
    op.drop_column('users', 'reset_token')

    # Drop email verification columns
    op.drop_column('users', 'verification_sent_at')
    op.drop_column('users', 'verification_token')
    op.drop_column('users', 'email_verified')
