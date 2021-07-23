# type: ignore

"""Add indexes on app_id, period_start for AppUsage events

Revision ID: 77dfcebf5290
Revises: 8258af8f3571
Create Date: 2021-07-23 14:00:36.269485

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "77dfcebf5290"
down_revision = "8258af8f3571"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "ix_daily_app_usage_app_id_started_at",
        "daily_app_usage_v3",
        ["app_id", "period_start"],
        unique=False,
        postgresql_ops={"app_id": "varchar_pattern_ops"},
    )
    op.create_index(
        "ix_monthly_app_usage_app_id_started_at",
        "monthly_app_usage_v3",
        ["app_id", "period_start"],
        unique=False,
        postgresql_ops={"app_id": "varchar_pattern_ops"},
    )


def downgrade():
    op.drop_index(
        "ix_monthly_app_usage_app_id_started_at",
        table_name="monthly_app_usage_v3",
        postgresql_ops={"app_id": "varchar_pattern_ops"},
    )
    op.drop_index(
        "ix_daily_app_usage_app_id_started_at",
        table_name="daily_app_usage_v3",
        postgresql_ops={"app_id": "varchar_pattern_ops"},
    )
