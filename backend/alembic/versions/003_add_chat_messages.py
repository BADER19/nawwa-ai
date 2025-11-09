"""Add chat messages table for conversation history

Revision ID: 003
Revises: 002
Create Date: 2025-11-02 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('workspace_id', sa.Integer(), nullable=True),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('visualization_spec', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('interpreter_source', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('idx_chat_user_created', 'chat_messages', ['user_id', 'created_at'], unique=False)
    op.create_index('idx_chat_workspace', 'chat_messages', ['workspace_id', 'created_at'], unique=False)
    op.create_index(op.f('ix_chat_messages_id'), 'chat_messages', ['id'], unique=False)
    op.create_index(op.f('ix_chat_messages_user_id'), 'chat_messages', ['user_id'], unique=False)
    op.create_index(op.f('ix_chat_messages_workspace_id'), 'chat_messages', ['workspace_id'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_chat_messages_workspace_id'), table_name='chat_messages')
    op.drop_index(op.f('ix_chat_messages_user_id'), table_name='chat_messages')
    op.drop_index(op.f('ix_chat_messages_id'), table_name='chat_messages')
    op.drop_index('idx_chat_workspace', table_name='chat_messages')
    op.drop_index('idx_chat_user_created', table_name='chat_messages')

    # Drop table
    op.drop_table('chat_messages')
