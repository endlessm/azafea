# type: ignore

"""Add CacheHasInvalidElements and StartupFinished events

Revision ID: eba4a3cf4aae
Revises: 9184d25ca795
Create Date: 2020-07-14 21:04:54.123331

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eba4a3cf4aae'
down_revision = '9184d25ca795'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'cache_has_invalid_elements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('number_of_valid_elements', sa.BigInteger(), nullable=False),
        sa.Column('number_of_bytes_read', sa.BigInteger(), nullable=False),
        sa.Column('request_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['request_id'], ['metrics_request_v2.id'],
            name=op.f('fk_cache_has_invalid_elements_request_id_metrics_request_v2')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_cache_has_invalid_elements'))
    )
    op.create_index(
        op.f('ix_cache_has_invalid_elements_request_id'), 'cache_has_invalid_elements',
        ['request_id'], unique=False)
    op.create_table(
        'startup_finished',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('firmware', sa.BigInteger(), nullable=False),
        sa.Column('loader', sa.BigInteger(), nullable=False),
        sa.Column('kernel', sa.BigInteger(), nullable=False),
        sa.Column('initrd', sa.BigInteger(), nullable=False),
        sa.Column('userspace', sa.BigInteger(), nullable=False),
        sa.Column('total', sa.BigInteger(), nullable=False),
        sa.Column('request_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['request_id'], ['metrics_request_v2.id'],
            name=op.f('fk_startup_finished_request_id_metrics_request_v2')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_startup_finished'))
    )
    op.create_index(
        op.f('ix_startup_finished_request_id'), 'startup_finished', ['request_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_startup_finished_request_id'), table_name='startup_finished')
    op.drop_table('startup_finished')
    op.drop_index(
        op.f('ix_cache_has_invalid_elements_request_id'), table_name='cache_has_invalid_elements')
    op.drop_table('cache_has_invalid_elements')
