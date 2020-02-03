# type: ignore

"""Store the parsed image components

Revision ID: 439e90a6874a
Revises: 0b3c2b3ae466
Create Date: 2020-02-03 16:11:50.418656

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '439e90a6874a'
down_revision = '0b3c2b3ae466'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('ping_configuration_v1', sa.Column('image_product', sa.Unicode(), nullable=True))
    op.add_column('ping_configuration_v1', sa.Column('image_branch', sa.Unicode(), nullable=True))
    op.add_column('ping_configuration_v1', sa.Column('image_arch', sa.Unicode(), nullable=True))
    op.add_column('ping_configuration_v1', sa.Column('image_platform', sa.Unicode(), nullable=True))
    op.add_column('ping_configuration_v1', sa.Column('image_timestamp', sa.DateTime(timezone=True),
                                                     nullable=True))
    op.add_column('ping_configuration_v1', sa.Column('image_personality', sa.Unicode(),
                                                     nullable=True))

    op.create_index(op.f('ix_ping_configuration_v1_image_product'), 'ping_configuration_v1',
                    ['image_product'], unique=False)
    op.create_index(op.f('ix_ping_configuration_v1_image_branch'), 'ping_configuration_v1',
                    ['image_branch'], unique=False)
    op.create_index(op.f('ix_ping_configuration_v1_image_arch'), 'ping_configuration_v1',
                    ['image_arch'], unique=False)
    op.create_index(op.f('ix_ping_configuration_v1_image_platform'), 'ping_configuration_v1',
                    ['image_platform'], unique=False)
    op.create_index(op.f('ix_ping_configuration_v1_image_timestamp'), 'ping_configuration_v1',
                    ['image_timestamp'], unique=False)
    op.create_index(op.f('ix_ping_configuration_v1_image_personality'), 'ping_configuration_v1',
                    ['image_personality'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_ping_configuration_v1_image_product'),
                  table_name='ping_configuration_v1')
    op.drop_index(op.f('ix_ping_configuration_v1_image_branch'), table_name='ping_configuration_v1')
    op.drop_index(op.f('ix_ping_configuration_v1_image_arch'), table_name='ping_configuration_v1')
    op.drop_index(op.f('ix_ping_configuration_v1_image_platform'),
                  table_name='ping_configuration_v1')
    op.drop_index(op.f('ix_ping_configuration_v1_image_timestamp'),
                  table_name='ping_configuration_v1')
    op.drop_index(op.f('ix_ping_configuration_v1_image_personality'),
                  table_name='ping_configuration_v1')

    op.drop_column('ping_configuration_v1', 'image_product')
    op.drop_column('ping_configuration_v1', 'image_branch')
    op.drop_column('ping_configuration_v1', 'image_arch')
    op.drop_column('ping_configuration_v1', 'image_platform')
    op.drop_column('ping_configuration_v1', 'image_timestamp')
    op.drop_column('ping_configuration_v1', 'image_personality')
