# type: ignore

"""Add request model

Revision ID: 8258af8f3571
Revises: 112b12fa4dc5
Create Date: 2021-07-22 09:58:12.007690

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8258af8f3571"
down_revision = "112b12fa4dc5"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "metrics_request_v3",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sha512", sa.Unicode(), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("absolute_timestamp", sa.BigInteger(), nullable=False),
        sa.Column("relative_timestamp", sa.BigInteger(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel_v3.id"],
            name=op.f("fk_metrics_request_v3_channel_id_channel_v3"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_metrics_request_v3")),
        sa.UniqueConstraint("sha512", name=op.f("uq_metrics_request_v3_sha512")),
    )
    op.create_index(
        op.f("ix_metrics_request_v3_channel_id"),
        "metrics_request_v3",
        ["channel_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_metrics_request_v3_channel_id"), table_name="metrics_request_v3"
    )
    op.drop_table("metrics_request_v3")
