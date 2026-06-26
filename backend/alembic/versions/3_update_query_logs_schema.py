"""update_query_logs_schema

Revision ID: update_query_logs
Revises: 0f7a8c9b1d2e
Create Date: 2026-05-19 10:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3_update_query_logs_schema'
down_revision: Union[str, None] = '2_add_lawyers_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop old index
    op.drop_index('ix_query_logs_session_id', table_name='query_logs')
    
    # Drop old columns
    op.drop_column('query_logs', 'user_id')
    op.drop_column('query_logs', 'session_id')
    op.drop_column('query_logs', 'intent_detected')
    op.drop_column('query_logs', 'sections_cited')
    op.drop_column('query_logs', 'ai_provider_used')
    op.drop_column('query_logs', 'response_time_ms')
    
    # Add new columns
    op.add_column('query_logs', sa.Column('response_text', sa.Text(), nullable=True))
    op.add_column('query_logs', sa.Column('category', sa.String(length=100), nullable=True))
    op.add_column('query_logs', sa.Column('state', sa.String(length=100), nullable=True))
    op.add_column('query_logs', sa.Column('provider', sa.String(length=50), nullable=True))
    op.add_column('query_logs', sa.Column('confidence_score', sa.Float(), nullable=True))
    op.add_column('query_logs', sa.Column('lang', sa.String(length=10), nullable=True))
    op.add_column('query_logs', sa.Column('response_time_ms', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('query_logs', 'response_time_ms')
    op.drop_column('query_logs', 'lang')
    op.drop_column('query_logs', 'confidence_score')
    op.drop_column('query_logs', 'provider')
    op.drop_column('query_logs', 'state')
    op.drop_column('query_logs', 'category')
    op.drop_column('query_logs', 'response_text')
    
    op.add_column('query_logs', sa.Column('response_time_ms', sa.Integer(), nullable=True))
    op.add_column('query_logs', sa.Column('ai_provider_used', sa.String(length=50), nullable=True))
    op.add_column('query_logs', sa.Column('sections_cited', sa.Text(), nullable=True))
    op.add_column('query_logs', sa.Column('intent_detected', sa.String(length=100), nullable=True))
    op.add_column('query_logs', sa.Column('session_id', sa.String(length=100), nullable=True))
    op.add_column('query_logs', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_index('ix_query_logs_session_id', 'query_logs', ['session_id'], unique=False)
