"""add_lawyers_table

Revision ID: 0f7a8c9b1d2e
Revises: 9d2cc7087ac4
Create Date: 2026-05-19 10:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2_add_lawyers_table'
down_revision: Union[str, None] = '9d2cc7087ac4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('lawyers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('full_name', sa.String(length=200), nullable=False),
    sa.Column('specialization', sa.String(length=200), nullable=False),
    sa.Column('location', sa.String(length=200), nullable=False),
    sa.Column('experience_years', sa.Integer(), nullable=True),
    sa.Column('bio', sa.Text(), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('profile_image_url', sa.String(length=500), nullable=True),
    sa.Column('rating', sa.Integer(), nullable=False, server_default='5'),
    sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('lawyer_inquiries',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('lawyer_id', sa.Integer(), nullable=False),
    sa.Column('user_name', sa.String(length=200), nullable=False),
    sa.Column('user_phone', sa.String(length=20), nullable=False),
    sa.Column('query_summary', sa.Text(), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['lawyer_id'], ['lawyers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('lawyer_inquiries')
    op.drop_table('lawyers')
