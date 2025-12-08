"""initial schema

Revision ID: 8e1644e7ce8c
Revises: 
Create Date: 2025-01-07 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8e1644e7ce8c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create initial schema from models
    # This migration serves as the initial migration, creating all tables
    
    # Create usage_metrics table
    op.create_table(
        'usage_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(), nullable=False),
        sa.Column('model', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('requests', sa.Integer(), nullable=False),
        sa.Column('tokens', sa.Integer(), nullable=False),
        sa.Column('errors', sa.Integer(), nullable=False),
        sa.Column('rate_limit_hits', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_usage_metrics_id', 'usage_metrics', ['id'], unique=False)
    op.create_index('ix_usage_metrics_provider', 'usage_metrics', ['provider'], unique=False)
    op.create_index('ix_usage_metrics_model', 'usage_metrics', ['model'], unique=False)
    op.create_index('ix_usage_metrics_timestamp', 'usage_metrics', ['timestamp'], unique=False)
    
    # Create model_rate_limits table
    op.create_table(
        'model_rate_limits',
        sa.Column('provider', sa.String(), nullable=False),
        sa.Column('model', sa.String(), nullable=False),
        sa.Column('per_minute', sa.Integer(), nullable=False),
        sa.Column('per_day', sa.Integer(), nullable=False),
        sa.Column('remaining_per_minute', sa.Integer(), nullable=False),
        sa.Column('remaining_per_day', sa.Integer(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('provider', 'model')
    )
    
    # Create provider_state table
    op.create_table(
        'provider_state',
        sa.Column('provider', sa.String(), nullable=False),
        sa.Column('healthy', sa.Boolean(), nullable=False),
        sa.Column('available', sa.Boolean(), nullable=False),
        sa.Column('error_count', sa.Integer(), nullable=False),
        sa.Column('success_count', sa.Integer(), nullable=False),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('provider')
    )
    
    # Create task_classifications table
    op.create_table(
        'task_classifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('request_id', sa.String(), nullable=True),
        sa.Column('task_type', sa.String(), nullable=False),
        sa.Column('confidence', sa.Integer(), nullable=False),
        sa.Column('factors', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_task_classifications_id', 'task_classifications', ['id'], unique=False)
    op.create_index('ix_task_classifications_request_id', 'task_classifications', ['request_id'], unique=False)
    op.create_index('ix_task_classifications_timestamp', 'task_classifications', ['timestamp'], unique=False)
    
    # Create model_selections table
    op.create_table(
        'model_selections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('request_id', sa.String(), nullable=True),
        sa.Column('task_type', sa.String(), nullable=False),
        sa.Column('selected_provider', sa.String(), nullable=False),
        sa.Column('selected_model', sa.String(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('benchmark_score', sa.Integer(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_model_selections_id', 'model_selections', ['id'], unique=False)
    op.create_index('ix_model_selections_request_id', 'model_selections', ['request_id'], unique=False)
    op.create_index('ix_model_selections_timestamp', 'model_selections', ['timestamp'], unique=False)


def downgrade() -> None:
    # Drop all tables
    op.drop_table('model_selections')
    op.drop_table('task_classifications')
    op.drop_table('provider_state')
    op.drop_table('model_rate_limits')
    op.drop_table('usage_metrics')

