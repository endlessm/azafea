# type: ignore

"""Materialized view for metrics.

Revision ID: e7c7d5f2e4df
Revises: d4809698244a
Create Date: 2020-06-09 13:01:05.739571

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'e7c7d5f2e4df'
down_revision = 'd4809698244a'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "CREATE MATERIALIZED VIEW machine_ids_by_day (day, machine_id) AS "
        "SELECT DISTINCT received_at::date, machine_id FROM metrics_request_v2")


def downgrade():
    op.execute("DROP MATERIALIZED VIEW machine_ids_by_day")
