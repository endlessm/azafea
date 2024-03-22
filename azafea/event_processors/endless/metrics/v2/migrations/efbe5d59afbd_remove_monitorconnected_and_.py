# type: ignore

"""Remove MonitorConnected and MonitorDisconnected events

Revision ID: efbe5d59afbd
Revises: 8eb67a73775b
Create Date: 2024-03-22 19:01:15.924816

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "efbe5d59afbd"
down_revision = "8eb67a73775b"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index("ix_monitor_connected_occured_at", table_name="monitor_connected")
    op.drop_index("ix_monitor_connected_request_id", table_name="monitor_connected")
    op.drop_table("monitor_connected")
    op.drop_index("ix_monitor_disconnected_occured_at", table_name="monitor_disconnected")
    op.drop_index("ix_monitor_disconnected_request_id", table_name="monitor_disconnected")
    op.drop_table("monitor_disconnected")


def downgrade():
    op.create_table(
        "monitor_disconnected",
        sa.Column("id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("user_id", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.Column(
            "occured_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False
        ),
        sa.Column("display_name", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("display_vendor", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("display_product", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("display_width", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("display_height", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("edid", postgresql.BYTEA(), autoincrement=False, nullable=False),
        sa.Column("request_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["request_id"],
            ["metrics_request_v2.id"],
            name="fk_monitor_disconnected_request_id_metrics_request_v2",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_monitor_disconnected"),
    )
    op.create_index(
        "ix_monitor_disconnected_request_id", "monitor_disconnected", ["request_id"], unique=False
    )
    op.create_index(
        "ix_monitor_disconnected_occured_at", "monitor_disconnected", ["occured_at"], unique=False
    )
    op.create_table(
        "monitor_connected",
        sa.Column("id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("user_id", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.Column(
            "occured_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False
        ),
        sa.Column("display_name", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("display_vendor", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("display_product", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("display_width", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("display_height", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("edid", postgresql.BYTEA(), autoincrement=False, nullable=False),
        sa.Column("request_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["request_id"],
            ["metrics_request_v2.id"],
            name="fk_monitor_connected_request_id_metrics_request_v2",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_monitor_connected"),
    )
    op.create_index(
        "ix_monitor_connected_request_id", "monitor_connected", ["request_id"], unique=False
    )
    op.create_index(
        "ix_monitor_connected_occured_at", "monitor_connected", ["occured_at"], unique=False
    )
