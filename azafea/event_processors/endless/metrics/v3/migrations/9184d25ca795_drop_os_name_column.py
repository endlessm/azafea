# type: ignore

"""Drop OS name column

Revision ID: 9184d25ca795
Revises: d4809698244a
Create Date: 2020-05-11 16:53:31.556805

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9184d25ca795'
down_revision = 'd4809698244a'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('os_version', 'name')


def downgrade():
    op.add_column('os_version', sa.Column(
        'name', sa.VARCHAR(), autoincrement=False, nullable=False, default='Endless'))
