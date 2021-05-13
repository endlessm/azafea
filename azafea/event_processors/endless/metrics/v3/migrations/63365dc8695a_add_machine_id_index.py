# type: ignore

"""Add machine_id index on machine by day table

Revision ID: 63365dc8695a
Revises: 991574509c57
Create Date: 2021-02-09 10:19:30.719800

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '63365dc8695a'
down_revision = '991574509c57'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        op.f('ix_machine_ids_by_day_machine_id'), 'machine_ids_by_day', ['machine_id'],
        unique=False)


def downgrade():
    op.drop_index(op.f('ix_machine_ids_by_day_machine_id'), table_name='machine_ids_by_day')
