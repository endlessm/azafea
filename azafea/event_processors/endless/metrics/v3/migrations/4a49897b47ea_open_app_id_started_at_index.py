# type: ignore

"""Add an index to find the most used apps faster

Revision ID: 4a49897b47ea
Revises: 9bd33e9778fa
Create Date: 2020-04-30 12:39:16.338295

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '4a49897b47ea'
down_revision = '9bd33e9778fa'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        'ix_shell_app_is_open_app_id_started_at',
        'shell_app_is_open',
        ['started_at', 'app_id'],
        unique=False,
        postgresql_ops={'app_id': 'varchar_pattern_ops'},
    )


def downgrade():
    op.drop_index('ix_shell_app_is_open_app_id_started_at', table_name='shell_app_is_open')
