# type: ignore

"""Remove WindowsLicenseTables event

Revision ID: bdf8187f9f72
Revises: 2812f42544fa
Create Date: 2024-03-25 14:13:39.982929

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "bdf8187f9f72"
down_revision = "2812f42544fa"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index("ix_windows_license_tables_occured_at", table_name="windows_license_tables")
    op.drop_index("ix_windows_license_tables_request_id", table_name="windows_license_tables")
    op.drop_table("windows_license_tables")


def downgrade():
    op.create_table(
        "windows_license_tables",
        sa.Column("id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("user_id", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.Column(
            "occured_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False
        ),
        sa.Column("tables", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.Column("request_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["request_id"],
            ["metrics_request_v2.id"],
            name="fk_windows_license_tables_request_id_metrics_request_v2",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_windows_license_tables"),
    )
    op.create_index(
        "ix_windows_license_tables_request_id",
        "windows_license_tables",
        ["request_id"],
        unique=False,
    )
    op.create_index(
        "ix_windows_license_tables_occured_at",
        "windows_license_tables",
        ["occured_at"],
        unique=False,
    )
