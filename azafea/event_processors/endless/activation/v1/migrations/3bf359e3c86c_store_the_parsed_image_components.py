# type: ignore

"""Store the parsed image components

Revision ID: 3bf359e3c86c
Revises: 3666122efd41
Create Date: 2020-02-03 16:03:19.957783

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3bf359e3c86c'
down_revision = '3666122efd41'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('activation_v1', sa.Column('image_product', sa.Unicode(), nullable=True))
    op.add_column('activation_v1', sa.Column('image_branch', sa.Unicode(), nullable=True))
    op.add_column('activation_v1', sa.Column('image_arch', sa.Unicode(), nullable=True))
    op.add_column('activation_v1', sa.Column('image_platform', sa.Unicode(), nullable=True))
    op.add_column('activation_v1', sa.Column('image_timestamp', sa.DateTime(timezone=True),
                                             nullable=True))
    op.add_column('activation_v1', sa.Column('image_personality', sa.Unicode(), nullable=True))

    op.create_index(op.f('ix_activation_v1_image_product'), 'activation_v1', ['image_product'],
                    unique=False)
    op.create_index(op.f('ix_activation_v1_image_branch'), 'activation_v1', ['image_branch'],
                    unique=False)
    op.create_index(op.f('ix_activation_v1_image_arch'), 'activation_v1', ['image_arch'],
                    unique=False)
    op.create_index(op.f('ix_activation_v1_image_platform'), 'activation_v1', ['image_platform'],
                    unique=False)
    op.create_index(op.f('ix_activation_v1_image_timestamp'), 'activation_v1', ['image_timestamp'],
                    unique=False)
    op.create_index(op.f('ix_activation_v1_image_personality'), 'activation_v1',
                    ['image_personality'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_activation_v1_image_product'), table_name='activation_v1')
    op.drop_index(op.f('ix_activation_v1_image_branch'), table_name='activation_v1')
    op.drop_index(op.f('ix_activation_v1_image_arch'), table_name='activation_v1')
    op.drop_index(op.f('ix_activation_v1_image_platform'), table_name='activation_v1')
    op.drop_index(op.f('ix_activation_v1_image_timestamp'), table_name='activation_v1')
    op.drop_index(op.f('ix_activation_v1_image_personality'), table_name='activation_v1')

    op.drop_column('activation_v1', 'image_product')
    op.drop_column('activation_v1', 'image_branch')
    op.drop_column('activation_v1', 'image_arch')
    op.drop_column('activation_v1', 'image_platform')
    op.drop_column('activation_v1', 'image_timestamp')
    op.drop_column('activation_v1', 'image_personality')
