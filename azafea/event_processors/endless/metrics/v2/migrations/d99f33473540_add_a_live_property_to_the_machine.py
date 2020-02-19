# type: ignore

"""Add a live property to the machine

Revision ID: d99f33473540
Revises: cced14e41a46
Create Date: 2020-02-19 10:56:19.364093

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd99f33473540'
down_revision = 'cced14e41a46'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('metrics_machine', sa.Column('live', sa.Boolean(), nullable=True,
                                               server_default=sa.sql.expression.false()))


def downgrade():
    op.drop_column('metrics_machine', 'live')
