# type: ignore

"""Add a demo property to the machine

Revision ID: a6e10c2e3f79
Revises: b3ad0a81aa3c
Create Date: 2020-02-24 14:01:11.715316

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a6e10c2e3f79'
down_revision = 'b3ad0a81aa3c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('metrics_machine', sa.Column('demo', sa.Boolean(), nullable=True,
                                               server_default=sa.sql.expression.false()))


def downgrade():
    op.drop_column('metrics_machine', 'demo')
