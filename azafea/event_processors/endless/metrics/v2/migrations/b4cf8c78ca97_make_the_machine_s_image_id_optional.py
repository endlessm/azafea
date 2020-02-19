# type: ignore

"""Make the machine's image id optional

Revision ID: b4cf8c78ca97
Revises: 3dc06459fc41
Create Date: 2020-02-19 10:00:46.948624

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b4cf8c78ca97'
down_revision = '3dc06459fc41'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('metrics_machine', 'image_id', existing_type=sa.VARCHAR(), nullable=True)


def downgrade():
    op.alter_column('metrics_machine', 'image_id', existing_type=sa.VARCHAR(), nullable=False)
