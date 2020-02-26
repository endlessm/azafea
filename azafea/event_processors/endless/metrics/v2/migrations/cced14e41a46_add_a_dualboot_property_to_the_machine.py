# type: ignore

"""Add a dualboot property to the machine

Revision ID: cced14e41a46
Revises: b4cf8c78ca97
Create Date: 2020-02-19 10:44:24.683813

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cced14e41a46'
down_revision = 'b4cf8c78ca97'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('metrics_machine', sa.Column('dualboot', sa.Boolean(), nullable=True,
                                               server_default=sa.sql.expression.false()))


def downgrade():
    op.drop_column('metrics_machine', 'dualboot')
