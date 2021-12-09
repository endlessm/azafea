# type: ignore

"""Add split flatpak repo stats event

Revision ID: 63f2d8b9636e
Revises: 05e5217f019f
Create Date: 2021-12-09 13:29:51.091862

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '63f2d8b9636e'
down_revision = '05e5217f019f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'split_flatpak_repo_stats_v3',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('os_version', sa.Unicode(), nullable=False),
        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('elapsed', sa.Interval(), nullable=False),
        sa.Column('num_os_refs', sa.Integer(), nullable=False),
        sa.Column('num_flatpak_refs', sa.Integer(), nullable=False),
        sa.Column('num_other_refs', sa.Integer(), nullable=False),
        sa.Column('num_objects', sa.Integer(), nullable=False),
        sa.Column('num_deltas', sa.Integer(), nullable=False),
        sa.Column('num_apps', sa.Integer(), nullable=False),
        sa.Column('size_apps', sa.BigInteger(), nullable=False),
        sa.Column('num_runtimes', sa.Integer(), nullable=False),
        sa.Column('size_runtimes', sa.BigInteger(), nullable=False),
        sa.Column('channel_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['channel_id'], ['channel_v3.id'],
            name=op.f(
                'fk_split_flatpak_repo_stats_v3_channel_id_channel_v3'
            )
        ),
        sa.PrimaryKeyConstraint(
            'id',
            name=op.f('pk_split_flatpak_repo_stats_v3')
        )
    )
    op.create_index(
        op.f('ix_split_flatpak_repo_stats_v3_channel_id'),
        'split_flatpak_repo_stats_v3', ['channel_id'], unique=False
    )
    op.create_index(
        op.f('ix_split_flatpak_repo_stats_v3_occured_at'),
        'split_flatpak_repo_stats_v3', ['occured_at'], unique=False
    )


def downgrade():
    op.drop_index(
        op.f('ix_split_flatpak_repo_stats_v3_occured_at'),
        table_name='split_flatpak_repo_stats_v3'
    )
    op.drop_index(
        op.f('ix_split_flatpak_repo_stats_v3_channel_id'),
        table_name='split_flatpak_repo_stats_v3'
    )
    op.drop_table('split_flatpak_repo_stats_v3')
