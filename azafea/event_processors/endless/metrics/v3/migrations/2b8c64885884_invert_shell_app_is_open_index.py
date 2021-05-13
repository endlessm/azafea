# type: ignore

"""Invert ShellAppIsOpen index

Revision ID: 2b8c64885884
Revises: 9184d25ca795
Create Date: 2020-07-13 17:41:40.851331

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '2b8c64885884'
down_revision = '9184d25ca795'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index('ix_shell_app_is_open_app_id_started_at', table_name='shell_app_is_open')
    op.create_index(
        'ix_shell_app_is_open_app_id_started_at',
        'shell_app_is_open',
        ['app_id', 'started_at'],
        unique=False,
        postgresql_ops={'app_id': 'varchar_pattern_ops'},
    )


def downgrade():
    op.drop_index('ix_shell_app_is_open_app_id_started_at', table_name='shell_app_is_open')
    op.create_index(
        'ix_shell_app_is_open_app_id_started_at',
        'shell_app_is_open',
        ['started_at', 'app_id'],
        unique=False,
        postgresql_ops={'app_id': 'varchar_pattern_ops'},
    )
