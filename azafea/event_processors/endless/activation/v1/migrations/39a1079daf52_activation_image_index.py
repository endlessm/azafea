# type: ignore

"""Activation image index.

Revision ID: 39a1079daf52
Revises: 3bf359e3c86c
Create Date: 2020-07-08 13:39:34.620812

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '39a1079daf52'
down_revision = '3bf359e3c86c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(op.f('ix_activation_v1_image'), 'activation_v1', ['image'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_activation_v1_image'), table_name='activation_v1')
