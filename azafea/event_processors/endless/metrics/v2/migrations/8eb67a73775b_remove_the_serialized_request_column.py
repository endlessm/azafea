# type: ignore

"""Remove the serialized request column

Revision ID: 8eb67a73775b
Revises: 63365dc8695a
Create Date: 2020-01-07 14:12:24.190678

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8eb67a73775b'
down_revision = '63365dc8695a'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('metrics_request_v2', 'serialized')


def downgrade():
    op.add_column('metrics_request_v2', sa.Column('serialized', postgresql.BYTEA(),
                                                  autoincrement=False, nullable=True))
