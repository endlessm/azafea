# type: ignore

"""Add day index on machine by day table

Revision ID: 29c26262aa70
Revises: 53fffde5ad55
Create Date: 2020-11-23 15:45:15.542680

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '29c26262aa70'
down_revision = '53fffde5ad55'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(op.f('ix_machine_ids_by_day_day'), 'machine_ids_by_day', ['day'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_machine_ids_by_day_day'), table_name='machine_ids_by_day')
