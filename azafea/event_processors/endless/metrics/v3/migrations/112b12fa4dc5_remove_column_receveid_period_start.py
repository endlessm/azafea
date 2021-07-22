# type: ignore

"""Remove column receveid_period_start

Revision ID: 112b12fa4dc5
Revises: a82a26763a82
Create Date: 2021-07-22 09:40:38.102573

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '112b12fa4dc5'
down_revision = 'a82a26763a82'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('invalid_aggregate_event_v3', 'receveid_period_start')
    op.drop_column('unknown_aggregate_event_v3', 'receveid_period_start')


def downgrade():
    op.add_column(
        'unknown_aggregate_event_v3',
        sa.Column('receveid_period_start', sa.VARCHAR(), autoincrement=False, nullable=True)
    )
    op.add_column(
        'invalid_aggregate_event_v3',
        sa.Column('receveid_period_start', sa.VARCHAR(), autoincrement=False, nullable=True)
    )
