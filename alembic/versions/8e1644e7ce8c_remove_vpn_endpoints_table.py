"""remove vpn_endpoints table

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
    # Drop vpn_endpoints table
    op.drop_table('vpn_endpoints')


def downgrade() -> None:
    # Recreate vpn_endpoints table (for rollback purposes)
    op.create_table(
        'vpn_endpoints',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('host', sa.String(), nullable=False),
        sa.Column('port', sa.Integer(), nullable=False),
        sa.Column('country', sa.String(), nullable=True),
        sa.Column('provider', sa.String(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

