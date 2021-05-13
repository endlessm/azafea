# type: ignore

"""Add the machine mapping table

Revision ID: 33c19f68197d
Revises: 1135ef61f61e
Create Date: 2019-12-11 11:09:39.562184

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '33c19f68197d'
down_revision = '1135ef61f61e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('metrics_machine',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('machine_id', sa.Unicode(length=32), nullable=False),
                    sa.Column('image_id', sa.Unicode(), nullable=False),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_metrics_machine')),
                    sa.UniqueConstraint('machine_id', name=op.f('uq_metrics_machine_machine_id')))


def downgrade():
    op.drop_table('metrics_machine')
