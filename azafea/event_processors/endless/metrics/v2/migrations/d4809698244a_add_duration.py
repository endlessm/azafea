# type: ignore

"""Add duration column to open shell apps

Revision ID: d4809698244a
Revises: 4a49897b47ea
Create Date: 2020-04-30 13:54:30.888222

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4809698244a'
down_revision = '4a49897b47ea'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('shell_app_is_open', sa.Column('duration', sa.Float(), nullable=True))
    op.execute('UPDATE shell_app_is_open SET duration = 0')
    op.alter_column('shell_app_is_open', 'duration', nullable=False)


def downgrade():
    op.drop_column('shell_app_is_open', 'duration')
