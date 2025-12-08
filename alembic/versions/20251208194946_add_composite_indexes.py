"""add composite indexes

Revision ID: 20251208194946
Revises: 8e1644e7ce8c
Create Date: 2025-12-08 19:49:46.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251208194946'
down_revision: Union[str, None] = '8e1644e7ce8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add composite indexes for common query patterns
    
    # Index on (provider, timestamp) for UsageMetrics - used for provider stats queries
    op.create_index(
        'ix_usage_metrics_provider_timestamp',
        'usage_metrics',
        ['provider', 'timestamp'],
        unique=False
    )
    
    # Index on (provider, model, timestamp) for UsageMetrics - used for model stats queries
    op.create_index(
        'ix_usage_metrics_provider_model_timestamp',
        'usage_metrics',
        ['provider', 'model', 'timestamp'],
        unique=False
    )


def downgrade() -> None:
    # Drop composite indexes
    op.drop_index('ix_usage_metrics_provider_model_timestamp', table_name='usage_metrics')
    op.drop_index('ix_usage_metrics_provider_timestamp', table_name='usage_metrics')

