# type: ignore

"""Add CheckpointBlocked tables

https://phabricator.endlessm.com/T35250

Revision ID: 9d6a1a667f01
Revises: 63f2d8b9636e
Create Date: 2024-03-22 15:12:40.762640

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9d6a1a667f01"
down_revision = "63f2d8b9636e"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "checkpoint_blocked_daily",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("os_version", sa.Unicode(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("count", sa.BigInteger(), nullable=False),
        sa.Column("vendor", sa.Unicode(), nullable=False),
        sa.Column("product", sa.Unicode(), nullable=False),
        sa.Column("booted_ref", sa.Unicode(), nullable=False),
        sa.Column("target_ref", sa.Unicode(), nullable=False),
        sa.Column("reason", sa.Unicode(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel_v3.id"],
            name=op.f("fk_checkpoint_blocked_daily_channel_id_channel_v3"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_checkpoint_blocked_daily")),
    )
    op.create_index(
        op.f("ix_checkpoint_blocked_daily_channel_id"),
        "checkpoint_blocked_daily",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_checkpoint_blocked_daily_period_start"),
        "checkpoint_blocked_daily",
        ["period_start"],
        unique=False,
    )
    op.create_table(
        "checkpoint_blocked_monthly",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("os_version", sa.Unicode(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("count", sa.BigInteger(), nullable=False),
        sa.Column("vendor", sa.Unicode(), nullable=False),
        sa.Column("product", sa.Unicode(), nullable=False),
        sa.Column("booted_ref", sa.Unicode(), nullable=False),
        sa.Column("target_ref", sa.Unicode(), nullable=False),
        sa.Column("reason", sa.Unicode(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel_v3.id"],
            name=op.f("fk_checkpoint_blocked_monthly_channel_id_channel_v3"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_checkpoint_blocked_monthly")),
    )
    op.create_index(
        op.f("ix_checkpoint_blocked_monthly_channel_id"),
        "checkpoint_blocked_monthly",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_checkpoint_blocked_monthly_period_start"),
        "checkpoint_blocked_monthly",
        ["period_start"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_checkpoint_blocked_monthly_period_start"),
        table_name="checkpoint_blocked_monthly",
    )
    op.drop_index(
        op.f("ix_checkpoint_blocked_monthly_channel_id"),
        table_name="checkpoint_blocked_monthly",
    )
    op.drop_table("checkpoint_blocked_monthly")
    op.drop_index(
        op.f("ix_checkpoint_blocked_daily_period_start"),
        table_name="checkpoint_blocked_daily",
    )
    op.drop_index(
        op.f("ix_checkpoint_blocked_daily_channel_id"),
        table_name="checkpoint_blocked_daily",
    )
    op.drop_table("checkpoint_blocked_daily")
