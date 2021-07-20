# type: ignore

"""Initial migrations for metrics v3

Revision ID: a82a26763a82
Revises:
Create Date: 2021-06-29 11:48:06.708222

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "a82a26763a82"
down_revision = None
branch_labels = ("metrics-3",)
depends_on = None


def upgrade():
    op.create_table(
        "channel_v3",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("image_id", sa.Unicode(), nullable=False),
        sa.Column("site", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("dual_boot", sa.Boolean(), nullable=False),
        sa.Column("live", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_channel_v3")),
        sa.UniqueConstraint(
            "image_id", "site", "dual_boot", "live", name=op.f("uq_channel_v3_image_id")
        ),
    )
    op.create_table(
        "computer_information_v3",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("os_version", sa.Unicode(), nullable=False),
        sa.Column("occured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("total_ram", sa.BigInteger(), nullable=False),
        sa.Column("total_disk", sa.BigInteger(), nullable=False),
        sa.Column("used_disk", sa.BigInteger(), nullable=False),
        sa.Column("free_disk", sa.BigInteger(), nullable=False),
        sa.Column("info", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel_v3.id"],
            name=op.f("fk_computer_information_v3_channel_id_channel_v3"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_computer_information_v3")),
    )
    op.create_index(
        op.f("ix_computer_information_v3_channel_id"),
        "computer_information_v3",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_computer_information_v3_occured_at"),
        "computer_information_v3",
        ["occured_at"],
        unique=False,
    )
    op.create_table(
        "daily_app_usage_v3",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("os_version", sa.Unicode(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("count", sa.BigInteger(), nullable=False),
        sa.Column("app_id", sa.Unicode(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel_v3.id"],
            name=op.f("fk_daily_app_usage_v3_channel_id_channel_v3"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_daily_app_usage_v3")),
    )
    op.create_index(
        op.f("ix_daily_app_usage_v3_channel_id"),
        "daily_app_usage_v3",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_daily_app_usage_v3_period_start"),
        "daily_app_usage_v3",
        ["period_start"],
        unique=False,
    )
    op.create_table(
        "daily_session_time_v3",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("os_version", sa.Unicode(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("count", sa.BigInteger(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel_v3.id"],
            name=op.f("fk_daily_session_time_v3_channel_id_channel_v3"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_daily_session_time_v3")),
    )
    op.create_index(
        op.f("ix_daily_session_time_v3_channel_id"),
        "daily_session_time_v3",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_daily_session_time_v3_period_start"),
        "daily_session_time_v3",
        ["period_start"],
        unique=False,
    )
    op.create_table(
        "daily_users_v3",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("os_version", sa.Unicode(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("count", sa.BigInteger(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel_v3.id"],
            name=op.f("fk_daily_users_v3_channel_id_channel_v3"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_daily_users_v3")),
    )
    op.create_index(
        op.f("ix_daily_users_v3_channel_id"),
        "daily_users_v3",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_daily_users_v3_period_start"),
        "daily_users_v3",
        ["period_start"],
        unique=False,
    )
    op.create_table(
        "invalid_aggregate_event_v3",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("os_version", sa.Unicode(), nullable=False),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payload_data", sa.LargeBinary(), nullable=False),
        sa.Column("error", sa.Unicode(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("count", sa.BigInteger(), nullable=False),
        sa.Column("receveid_period_start", sa.Unicode(), nullable=True),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel_v3.id"],
            name=op.f("fk_invalid_aggregate_event_v3_channel_id_channel_v3"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_invalid_aggregate_event_v3")),
    )
    op.create_index(
        op.f("ix_invalid_aggregate_event_v3_channel_id"),
        "invalid_aggregate_event_v3",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_invalid_aggregate_event_v3_period_start"),
        "invalid_aggregate_event_v3",
        ["period_start"],
        unique=False,
    )
    op.create_table(
        "invalid_singular_event_v3",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("os_version", sa.Unicode(), nullable=False),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payload_data", sa.LargeBinary(), nullable=False),
        sa.Column("error", sa.Unicode(), nullable=False),
        sa.Column("occured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel_v3.id"],
            name=op.f("fk_invalid_singular_event_v3_channel_id_channel_v3"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_invalid_singular_event_v3")),
    )
    op.create_index(
        op.f("ix_invalid_singular_event_v3_channel_id"),
        "invalid_singular_event_v3",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_invalid_singular_event_v3_occured_at"),
        "invalid_singular_event_v3",
        ["occured_at"],
        unique=False,
    )
    op.create_table(
        "launched_equivalent_existing_flatpak_v3",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("os_version", sa.Unicode(), nullable=False),
        sa.Column("occured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("replacement_app_id", sa.Unicode(), nullable=False),
        sa.Column("argv", sa.ARRAY(sa.Unicode(), dimensions=1), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel_v3.id"],
            name=op.f(
                "fk_launched_equivalent_existing_flatpak_v3_channel_id_channel_v3"
            ),
        ),
        sa.PrimaryKeyConstraint(
            "id", name=op.f("pk_launched_equivalent_existing_flatpak_v3")
        ),
    )
    op.create_index(
        op.f("ix_launched_equivalent_existing_flatpak_v3_channel_id"),
        "launched_equivalent_existing_flatpak_v3",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_launched_equivalent_existing_flatpak_v3_occured_at"),
        "launched_equivalent_existing_flatpak_v3",
        ["occured_at"],
        unique=False,
    )
    op.create_table(
        "launched_equivalent_installer_for_flatpak_v3",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("os_version", sa.Unicode(), nullable=False),
        sa.Column("occured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("replacement_app_id", sa.Unicode(), nullable=False),
        sa.Column("argv", sa.ARRAY(sa.Unicode(), dimensions=1), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel_v3.id"],
            name=op.f(
                "fk_launched_equivalent_installer_for_flatpak_v3_channel_id_channel_v3"
            ),
        ),
        sa.PrimaryKeyConstraint(
            "id", name=op.f("pk_launched_equivalent_installer_for_flatpak_v3")
        ),
    )
    op.create_index(
        op.f("ix_launched_equivalent_installer_for_flatpak_v3_channel_id"),
        "launched_equivalent_installer_for_flatpak_v3",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_launched_equivalent_installer_for_flatpak_v3_occured_at"),
        "launched_equivalent_installer_for_flatpak_v3",
        ["occured_at"],
        unique=False,
    )
    op.create_table(
        "launched_existing_flatpak_v3",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("os_version", sa.Unicode(), nullable=False),
        sa.Column("occured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("replacement_app_id", sa.Unicode(), nullable=False),
        sa.Column("argv", sa.ARRAY(sa.Unicode(), dimensions=1), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel_v3.id"],
            name=op.f("fk_launched_existing_flatpak_v3_channel_id_channel_v3"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_launched_existing_flatpak_v3")),
    )
    op.create_index(
        op.f("ix_launched_existing_flatpak_v3_channel_id"),
        "launched_existing_flatpak_v3",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_launched_existing_flatpak_v3_occured_at"),
        "launched_existing_flatpak_v3",
        ["occured_at"],
        unique=False,
    )
    op.create_table(
        "launched_installer_for_flatpak_v3",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("os_version", sa.Unicode(), nullable=False),
        sa.Column("occured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("replacement_app_id", sa.Unicode(), nullable=False),
        sa.Column("argv", sa.ARRAY(sa.Unicode(), dimensions=1), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel_v3.id"],
            name=op.f("fk_launched_installer_for_flatpak_v3_channel_id_channel_v3"),
        ),
        sa.PrimaryKeyConstraint(
            "id", name=op.f("pk_launched_installer_for_flatpak_v3")
        ),
    )
    op.create_index(
        op.f("ix_launched_installer_for_flatpak_v3_channel_id"),
        "launched_installer_for_flatpak_v3",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_launched_installer_for_flatpak_v3_occured_at"),
        "launched_installer_for_flatpak_v3",
        ["occured_at"],
        unique=False,
    )
    op.create_table(
        "linux_package_opened_v3",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("os_version", sa.Unicode(), nullable=False),
        sa.Column("occured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("argv", sa.ARRAY(sa.Unicode(), dimensions=1), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel_v3.id"],
            name=op.f("fk_linux_package_opened_v3_channel_id_channel_v3"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_linux_package_opened_v3")),
    )
    op.create_index(
        op.f("ix_linux_package_opened_v3_channel_id"),
        "linux_package_opened_v3",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_linux_package_opened_v3_occured_at"),
        "linux_package_opened_v3",
        ["occured_at"],
        unique=False,
    )
    op.create_table(
        "monthly_app_usage_v3",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("os_version", sa.Unicode(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("count", sa.BigInteger(), nullable=False),
        sa.Column("app_id", sa.Unicode(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel_v3.id"],
            name=op.f("fk_monthly_app_usage_v3_channel_id_channel_v3"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_monthly_app_usage_v3")),
    )
    op.create_index(
        op.f("ix_monthly_app_usage_v3_channel_id"),
        "monthly_app_usage_v3",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_monthly_app_usage_v3_period_start"),
        "monthly_app_usage_v3",
        ["period_start"],
        unique=False,
    )
    op.create_table(
        "monthly_session_time_v3",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("os_version", sa.Unicode(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("count", sa.BigInteger(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel_v3.id"],
            name=op.f("fk_monthly_session_time_v3_channel_id_channel_v3"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_monthly_session_time_v3")),
    )
    op.create_index(
        op.f("ix_monthly_session_time_v3_channel_id"),
        "monthly_session_time_v3",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_monthly_session_time_v3_period_start"),
        "monthly_session_time_v3",
        ["period_start"],
        unique=False,
    )
    op.create_table(
        "monthly_users_v3",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("os_version", sa.Unicode(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("count", sa.BigInteger(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel_v3.id"],
            name=op.f("fk_monthly_users_v3_channel_id_channel_v3"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_monthly_users_v3")),
    )
    op.create_index(
        op.f("ix_monthly_users_v3_channel_id"),
        "monthly_users_v3",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_monthly_users_v3_period_start"),
        "monthly_users_v3",
        ["period_start"],
        unique=False,
    )
    op.create_table(
        "parental_controls_blocked_flatpak_install_v3",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("os_version", sa.Unicode(), nullable=False),
        sa.Column("occured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("app", sa.Unicode(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel_v3.id"],
            name=op.f(
                "fk_parental_controls_blocked_flatpak_install_v3_channel_id_channel_v3"
            ),
        ),
        sa.PrimaryKeyConstraint(
            "id", name=op.f("pk_parental_controls_blocked_flatpak_install_v3")
        ),
    )
    op.create_index(
        op.f("ix_parental_controls_blocked_flatpak_install_v3_channel_id"),
        "parental_controls_blocked_flatpak_install_v3",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_parental_controls_blocked_flatpak_install_v3_occured_at"),
        "parental_controls_blocked_flatpak_install_v3",
        ["occured_at"],
        unique=False,
    )
    op.create_table(
        "parental_controls_blocked_flatpak_run_v3",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("os_version", sa.Unicode(), nullable=False),
        sa.Column("occured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("app", sa.Unicode(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel_v3.id"],
            name=op.f(
                "fk_parental_controls_blocked_flatpak_run_v3_channel_id_channel_v3"
            ),
        ),
        sa.PrimaryKeyConstraint(
            "id", name=op.f("pk_parental_controls_blocked_flatpak_run_v3")
        ),
    )
    op.create_index(
        op.f("ix_parental_controls_blocked_flatpak_run_v3_channel_id"),
        "parental_controls_blocked_flatpak_run_v3",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_parental_controls_blocked_flatpak_run_v3_occured_at"),
        "parental_controls_blocked_flatpak_run_v3",
        ["occured_at"],
        unique=False,
    )
    op.create_table(
        "parental_controls_changed_v3",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("os_version", sa.Unicode(), nullable=False),
        sa.Column("occured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("app_filter_is_whitelist", sa.Boolean(), nullable=False),
        sa.Column("app_filter", sa.ARRAY(sa.Unicode(), dimensions=1), nullable=False),
        sa.Column(
            "oars_filter", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("allow_user_installation", sa.Boolean(), nullable=False),
        sa.Column("allow_system_installation", sa.Boolean(), nullable=False),
        sa.Column("is_administrator", sa.Boolean(), nullable=False),
        sa.Column("is_initial_setup", sa.Boolean(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel_v3.id"],
            name=op.f("fk_parental_controls_changed_v3_channel_id_channel_v3"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_parental_controls_changed_v3")),
    )
    op.create_index(
        op.f("ix_parental_controls_changed_v3_channel_id"),
        "parental_controls_changed_v3",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_parental_controls_changed_v3_occured_at"),
        "parental_controls_changed_v3",
        ["occured_at"],
        unique=False,
    )
    op.create_table(
        "parental_controls_enabled_v3",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("os_version", sa.Unicode(), nullable=False),
        sa.Column("occured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel_v3.id"],
            name=op.f("fk_parental_controls_enabled_v3_channel_id_channel_v3"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_parental_controls_enabled_v3")),
    )
    op.create_index(
        op.f("ix_parental_controls_enabled_v3_channel_id"),
        "parental_controls_enabled_v3",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_parental_controls_enabled_v3_occured_at"),
        "parental_controls_enabled_v3",
        ["occured_at"],
        unique=False,
    )
    op.create_table(
        "program_dumped_core_v3",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("os_version", sa.Unicode(), nullable=False),
        sa.Column("occured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("info", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel_v3.id"],
            name=op.f("fk_program_dumped_core_v3_channel_id_channel_v3"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_program_dumped_core_v3")),
    )
    op.create_index(
        op.f("ix_program_dumped_core_v3_channel_id"),
        "program_dumped_core_v3",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_program_dumped_core_v3_occured_at"),
        "program_dumped_core_v3",
        ["occured_at"],
        unique=False,
    )
    op.create_table(
        "startup_finished_v3",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("os_version", sa.Unicode(), nullable=False),
        sa.Column("occured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("firmware", sa.BigInteger(), nullable=False),
        sa.Column("loader", sa.BigInteger(), nullable=False),
        sa.Column("kernel", sa.BigInteger(), nullable=False),
        sa.Column("initrd", sa.BigInteger(), nullable=False),
        sa.Column("userspace", sa.BigInteger(), nullable=False),
        sa.Column("total", sa.BigInteger(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel_v3.id"],
            name=op.f("fk_startup_finished_v3_channel_id_channel_v3"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_startup_finished_v3")),
    )
    op.create_index(
        op.f("ix_startup_finished_v3_channel_id"),
        "startup_finished_v3",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_startup_finished_v3_occured_at"),
        "startup_finished_v3",
        ["occured_at"],
        unique=False,
    )
    op.create_table(
        "unknown_aggregate_event_v3",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("os_version", sa.Unicode(), nullable=False),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payload_data", sa.LargeBinary(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("count", sa.BigInteger(), nullable=False),
        sa.Column("receveid_period_start", sa.Unicode(), nullable=True),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel_v3.id"],
            name=op.f("fk_unknown_aggregate_event_v3_channel_id_channel_v3"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_unknown_aggregate_event_v3")),
    )
    op.create_index(
        op.f("ix_unknown_aggregate_event_v3_channel_id"),
        "unknown_aggregate_event_v3",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_unknown_aggregate_event_v3_period_start"),
        "unknown_aggregate_event_v3",
        ["period_start"],
        unique=False,
    )
    op.create_table(
        "unknown_singular_event_v3",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("os_version", sa.Unicode(), nullable=False),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payload_data", sa.LargeBinary(), nullable=False),
        sa.Column("occured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel_v3.id"],
            name=op.f("fk_unknown_singular_event_v3_channel_id_channel_v3"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_unknown_singular_event_v3")),
    )
    op.create_index(
        op.f("ix_unknown_singular_event_v3_channel_id"),
        "unknown_singular_event_v3",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_unknown_singular_event_v3_occured_at"),
        "unknown_singular_event_v3",
        ["occured_at"],
        unique=False,
    )
    op.create_table(
        "updater_failure_v3",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("os_version", sa.Unicode(), nullable=False),
        sa.Column("occured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("component", sa.Unicode(), nullable=False),
        sa.Column("error_message", sa.Unicode(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel_v3.id"],
            name=op.f("fk_updater_failure_v3_channel_id_channel_v3"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_updater_failure_v3")),
    )
    op.create_index(
        op.f("ix_updater_failure_v3_channel_id"),
        "updater_failure_v3",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_updater_failure_v3_occured_at"),
        "updater_failure_v3",
        ["occured_at"],
        unique=False,
    )
    op.create_table(
        "windows_app_opened_v3",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("os_version", sa.Unicode(), nullable=False),
        sa.Column("occured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("argv", sa.ARRAY(sa.Unicode(), dimensions=1), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channel_v3.id"],
            name=op.f("fk_windows_app_opened_v3_channel_id_channel_v3"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_windows_app_opened_v3")),
    )
    op.create_index(
        op.f("ix_windows_app_opened_v3_channel_id"),
        "windows_app_opened_v3",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_windows_app_opened_v3_occured_at"),
        "windows_app_opened_v3",
        ["occured_at"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_windows_app_opened_v3_occured_at"), table_name="windows_app_opened_v3"
    )
    op.drop_index(
        op.f("ix_windows_app_opened_v3_channel_id"), table_name="windows_app_opened_v3"
    )
    op.drop_table("windows_app_opened_v3")
    op.drop_index(
        op.f("ix_updater_failure_v3_occured_at"), table_name="updater_failure_v3"
    )
    op.drop_index(
        op.f("ix_updater_failure_v3_channel_id"), table_name="updater_failure_v3"
    )
    op.drop_table("updater_failure_v3")
    op.drop_index(
        op.f("ix_unknown_singular_event_v3_occured_at"),
        table_name="unknown_singular_event_v3",
    )
    op.drop_index(
        op.f("ix_unknown_singular_event_v3_channel_id"),
        table_name="unknown_singular_event_v3",
    )
    op.drop_table("unknown_singular_event_v3")
    op.drop_index(
        op.f("ix_unknown_aggregate_event_v3_period_start"),
        table_name="unknown_aggregate_event_v3",
    )
    op.drop_index(
        op.f("ix_unknown_aggregate_event_v3_channel_id"),
        table_name="unknown_aggregate_event_v3",
    )
    op.drop_table("unknown_aggregate_event_v3")
    op.drop_index(
        op.f("ix_startup_finished_v3_occured_at"), table_name="startup_finished_v3"
    )
    op.drop_index(
        op.f("ix_startup_finished_v3_channel_id"), table_name="startup_finished_v3"
    )
    op.drop_table("startup_finished_v3")
    op.drop_index(
        op.f("ix_program_dumped_core_v3_occured_at"),
        table_name="program_dumped_core_v3",
    )
    op.drop_index(
        op.f("ix_program_dumped_core_v3_channel_id"),
        table_name="program_dumped_core_v3",
    )
    op.drop_table("program_dumped_core_v3")
    op.drop_index(
        op.f("ix_parental_controls_enabled_v3_occured_at"),
        table_name="parental_controls_enabled_v3",
    )
    op.drop_index(
        op.f("ix_parental_controls_enabled_v3_channel_id"),
        table_name="parental_controls_enabled_v3",
    )
    op.drop_table("parental_controls_enabled_v3")
    op.drop_index(
        op.f("ix_parental_controls_changed_v3_occured_at"),
        table_name="parental_controls_changed_v3",
    )
    op.drop_index(
        op.f("ix_parental_controls_changed_v3_channel_id"),
        table_name="parental_controls_changed_v3",
    )
    op.drop_table("parental_controls_changed_v3")
    op.drop_index(
        op.f("ix_parental_controls_blocked_flatpak_run_v3_occured_at"),
        table_name="parental_controls_blocked_flatpak_run_v3",
    )
    op.drop_index(
        op.f("ix_parental_controls_blocked_flatpak_run_v3_channel_id"),
        table_name="parental_controls_blocked_flatpak_run_v3",
    )
    op.drop_table("parental_controls_blocked_flatpak_run_v3")
    op.drop_index(
        op.f("ix_parental_controls_blocked_flatpak_install_v3_occured_at"),
        table_name="parental_controls_blocked_flatpak_install_v3",
    )
    op.drop_index(
        op.f("ix_parental_controls_blocked_flatpak_install_v3_channel_id"),
        table_name="parental_controls_blocked_flatpak_install_v3",
    )
    op.drop_table("parental_controls_blocked_flatpak_install_v3")
    op.drop_index(
        op.f("ix_monthly_users_v3_period_start"), table_name="monthly_users_v3"
    )
    op.drop_index(op.f("ix_monthly_users_v3_channel_id"), table_name="monthly_users_v3")
    op.drop_table("monthly_users_v3")
    op.drop_index(
        op.f("ix_monthly_session_time_v3_period_start"),
        table_name="monthly_session_time_v3",
    )
    op.drop_index(
        op.f("ix_monthly_session_time_v3_channel_id"),
        table_name="monthly_session_time_v3",
    )
    op.drop_table("monthly_session_time_v3")
    op.drop_index(
        op.f("ix_monthly_app_usage_v3_period_start"), table_name="monthly_app_usage_v3"
    )
    op.drop_index(
        op.f("ix_monthly_app_usage_v3_channel_id"), table_name="monthly_app_usage_v3"
    )
    op.drop_table("monthly_app_usage_v3")
    op.drop_index(
        op.f("ix_linux_package_opened_v3_occured_at"),
        table_name="linux_package_opened_v3",
    )
    op.drop_index(
        op.f("ix_linux_package_opened_v3_channel_id"),
        table_name="linux_package_opened_v3",
    )
    op.drop_table("linux_package_opened_v3")
    op.drop_index(
        op.f("ix_launched_installer_for_flatpak_v3_occured_at"),
        table_name="launched_installer_for_flatpak_v3",
    )
    op.drop_index(
        op.f("ix_launched_installer_for_flatpak_v3_channel_id"),
        table_name="launched_installer_for_flatpak_v3",
    )
    op.drop_table("launched_installer_for_flatpak_v3")
    op.drop_index(
        op.f("ix_launched_existing_flatpak_v3_occured_at"),
        table_name="launched_existing_flatpak_v3",
    )
    op.drop_index(
        op.f("ix_launched_existing_flatpak_v3_channel_id"),
        table_name="launched_existing_flatpak_v3",
    )
    op.drop_table("launched_existing_flatpak_v3")
    op.drop_index(
        op.f("ix_launched_equivalent_installer_for_flatpak_v3_occured_at"),
        table_name="launched_equivalent_installer_for_flatpak_v3",
    )
    op.drop_index(
        op.f("ix_launched_equivalent_installer_for_flatpak_v3_channel_id"),
        table_name="launched_equivalent_installer_for_flatpak_v3",
    )
    op.drop_table("launched_equivalent_installer_for_flatpak_v3")
    op.drop_index(
        op.f("ix_launched_equivalent_existing_flatpak_v3_occured_at"),
        table_name="launched_equivalent_existing_flatpak_v3",
    )
    op.drop_index(
        op.f("ix_launched_equivalent_existing_flatpak_v3_channel_id"),
        table_name="launched_equivalent_existing_flatpak_v3",
    )
    op.drop_table("launched_equivalent_existing_flatpak_v3")
    op.drop_index(
        op.f("ix_invalid_singular_event_v3_occured_at"),
        table_name="invalid_singular_event_v3",
    )
    op.drop_index(
        op.f("ix_invalid_singular_event_v3_channel_id"),
        table_name="invalid_singular_event_v3",
    )
    op.drop_table("invalid_singular_event_v3")
    op.drop_index(
        op.f("ix_invalid_aggregate_event_v3_period_start"),
        table_name="invalid_aggregate_event_v3",
    )
    op.drop_index(
        op.f("ix_invalid_aggregate_event_v3_channel_id"),
        table_name="invalid_aggregate_event_v3",
    )
    op.drop_table("invalid_aggregate_event_v3")
    op.drop_index(op.f("ix_daily_users_v3_period_start"), table_name="daily_users_v3")
    op.drop_index(op.f("ix_daily_users_v3_channel_id"), table_name="daily_users_v3")
    op.drop_table("daily_users_v3")
    op.drop_index(
        op.f("ix_daily_session_time_v3_period_start"),
        table_name="daily_session_time_v3",
    )
    op.drop_index(
        op.f("ix_daily_session_time_v3_channel_id"), table_name="daily_session_time_v3"
    )
    op.drop_table("daily_session_time_v3")
    op.drop_index(
        op.f("ix_daily_app_usage_v3_period_start"), table_name="daily_app_usage_v3"
    )
    op.drop_index(
        op.f("ix_daily_app_usage_v3_channel_id"), table_name="daily_app_usage_v3"
    )
    op.drop_table("daily_app_usage_v3")
    op.drop_index(
        op.f("ix_computer_information_v3_occured_at"),
        table_name="computer_information_v3",
    )
    op.drop_index(
        op.f("ix_computer_information_v3_channel_id"),
        table_name="computer_information_v3",
    )
    op.drop_table("computer_information_v3")
    op.drop_table("channel_v3")
