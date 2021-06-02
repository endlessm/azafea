# type: ignore

"""Remove serial and mac_hash from activation_v1

Revision ID: 3ce72dccdef8
Revises: 0e824c3dfc31
Create Date: 2021-06-02 11:05:58.047317

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3ce72dccdef8"
down_revision = "0e824c3dfc31"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("activation_v1", "serial")
    op.drop_column("activation_v1", "mac_hash")


def downgrade():
    op.add_column(
        "activation_v1",
        sa.Column("mac_hash", sa.BIGINT(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "activation_v1",
        sa.Column("serial", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
