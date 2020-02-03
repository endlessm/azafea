# type: ignore

"""Store the parsed image components as attributes of the machine

Revision ID: 3dc06459fc41
Revises: d0d01392a0ee
Create Date: 2020-02-03 13:55:47.869891

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3dc06459fc41'
down_revision = 'd0d01392a0ee'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('metrics_machine', sa.Column('image_product', sa.Unicode(), nullable=True))
    op.add_column('metrics_machine', sa.Column('image_branch', sa.Unicode(), nullable=True))
    op.add_column('metrics_machine', sa.Column('image_arch', sa.Unicode(), nullable=True))
    op.add_column('metrics_machine', sa.Column('image_platform', sa.Unicode(), nullable=True))
    op.add_column('metrics_machine', sa.Column('image_timestamp', sa.DateTime(timezone=True),
                                               nullable=True))
    op.add_column('metrics_machine', sa.Column('image_personality', sa.Unicode(), nullable=True))

    op.create_index(op.f('ix_metrics_machine_image_product'), 'metrics_machine', ['image_product'],
                    unique=False)
    op.create_index(op.f('ix_metrics_machine_image_branch'), 'metrics_machine', ['image_branch'],
                    unique=False)
    op.create_index(op.f('ix_metrics_machine_image_arch'), 'metrics_machine', ['image_arch'],
                    unique=False)
    op.create_index(op.f('ix_metrics_machine_image_platform'), 'metrics_machine',
                    ['image_platform'], unique=False)
    op.create_index(op.f('ix_metrics_machine_image_timestamp'), 'metrics_machine',
                    ['image_timestamp'], unique=False)
    op.create_index(op.f('ix_metrics_machine_image_personality'), 'metrics_machine',
                    ['image_personality'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_metrics_machine_image_product'), table_name='metrics_machine')
    op.drop_index(op.f('ix_metrics_machine_image_branch'), table_name='metrics_machine')
    op.drop_index(op.f('ix_metrics_machine_image_arch'), table_name='metrics_machine')
    op.drop_index(op.f('ix_metrics_machine_image_platform'), table_name='metrics_machine')
    op.drop_index(op.f('ix_metrics_machine_image_timestamp'), table_name='metrics_machine')
    op.drop_index(op.f('ix_metrics_machine_image_personality'), table_name='metrics_machine')

    op.drop_column('metrics_machine', 'image_product')
    op.drop_column('metrics_machine', 'image_branch')
    op.drop_column('metrics_machine', 'image_arch')
    op.drop_column('metrics_machine', 'image_platform')
    op.drop_column('metrics_machine', 'image_timestamp')
    op.drop_column('metrics_machine', 'image_personality')
