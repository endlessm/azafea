# type: ignore

"""Remove Uptime table

Revision ID: 2812f42544fa
Revises: efbe5d59afbd
Create Date: 2024-03-25 14:05:48.191366

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "2812f42544fa"
down_revision = "efbe5d59afbd"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index("ix_uptime_occured_at", table_name="uptime")
    op.drop_index("ix_uptime_request_id", table_name="uptime")
    op.drop_table("uptime")


def downgrade():
    op.create_table(
        "uptime",
        sa.Column("id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("user_id", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.Column(
            "occured_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False
        ),
        sa.Column("accumulated_uptime", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.Column("number_of_boots", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.Column("request_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["request_id"],
            ["metrics_request_v2.id"],
            name="fk_uptime_request_id_metrics_request_v2",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_uptime"),
    )
    op.create_index("ix_uptime_request_id", "uptime", ["request_id"], unique=False)
    op.create_index("ix_uptime_occured_at", "uptime", ["occured_at"], unique=False)
