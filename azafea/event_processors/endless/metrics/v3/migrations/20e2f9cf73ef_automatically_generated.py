# type: ignore

"""Automatically generated

Revision ID: 20e2f9cf73ef
Revises: 8258af8f3571
Create Date: 2021-07-27 15:44:41.869529

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '20e2f9cf73ef'
down_revision = ('8258af8f3571', '24a2bb2bf13e')
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        'CREATE  VIEW "launched_equivalent_existing_flatpak_view" AS SELECT anon_1.launched_equivalent_existing_flatpak_v3_occured_at AS anon_1_launched_equivalent_existing_flatpak_v3_occured_at, anon_1.launched_equivalent_existing_flatpak_v3_os_version AS anon_1_launched_equivalent_existing_flatpak_v3_os_version, anon_1.launched_equivalent_existing_flatpak_v3_replacement_app_id AS anon_1_launched_equivalent_existing_flatpak_v3_replacement_app_id, anon_1.launched_equivalent_existing_flatpak_v3_argv AS anon_1_launched_equivalent_existing_flatpak_v3_argv, anon_1.channel_v3_image_id AS anon_1_channel_v3_image_id, anon_1.channel_v3_site AS anon_1_channel_v3_site, anon_1.channel_v3_dual_boot AS anon_1_channel_v3_dual_boot, anon_1.channel_v3_live AS anon_1_channel_v3_live '
        'FROM (SELECT launched_equivalent_existing_flatpak_v3.occured_at AS launched_equivalent_existing_flatpak_v3_occured_at, launched_equivalent_existing_flatpak_v3.os_version AS launched_equivalent_existing_flatpak_v3_os_version, launched_equivalent_existing_flatpak_v3.replacement_app_id AS launched_equivalent_existing_flatpak_v3_replacement_app_id, launched_equivalent_existing_flatpak_v3.argv AS launched_equivalent_existing_flatpak_v3_argv, channel_v3.image_id AS channel_v3_image_id, channel_v3.site AS channel_v3_site, channel_v3.dual_boot AS channel_v3_dual_boot, channel_v3.live AS channel_v3_live '
        'FROM launched_equivalent_existing_flatpak_v3 JOIN channel_v3 ON channel_v3.id = launched_equivalent_existing_flatpak_v3.channel_id UNION ALL launched_equivalent_existing_flatpak_view_v2) AS anon_1'
    )
    op.execute(
        'CREATE  VIEW "launched_equivalent_installer_for_flatpak_view" AS SELECT anon_1.launched_equivalent_installer_for_flatpak_v3_occured_at AS anon_1_launched_equivalent_installer_for_flatpak_v3_occured_at, anon_1.launched_equivalent_installer_for_flatpak_v3_os_version AS anon_1_launched_equivalent_installer_for_flatpak_v3_os_version, anon_1.launched_equivalent_installer_for_flatpak_v3_replacement_app_id AS anon_1_launched_equivalent_installer_for_flatpak_v3_replacement_app_id, anon_1.launched_equivalent_installer_for_flatpak_v3_argv AS anon_1_launched_equivalent_installer_for_flatpak_v3_argv, anon_1.channel_v3_image_id AS anon_1_channel_v3_image_id, anon_1.channel_v3_site AS anon_1_channel_v3_site, anon_1.channel_v3_dual_boot AS anon_1_channel_v3_dual_boot, anon_1.channel_v3_live AS anon_1_channel_v3_live '
        'FROM (SELECT launched_equivalent_installer_for_flatpak_v3.occured_at AS launched_equivalent_installer_for_flatpak_v3_occured_at, launched_equivalent_installer_for_flatpak_v3.os_version AS launched_equivalent_installer_for_flatpak_v3_os_version, launched_equivalent_installer_for_flatpak_v3.replacement_app_id AS launched_equivalent_installer_for_flatpak_v3_replacement_app_id, launched_equivalent_installer_for_flatpak_v3.argv AS launched_equivalent_installer_for_flatpak_v3_argv, channel_v3.image_id AS channel_v3_image_id, channel_v3.site AS channel_v3_site, channel_v3.dual_boot AS channel_v3_dual_boot, channel_v3.live AS channel_v3_live '
        'FROM launched_equivalent_installer_for_flatpak_v3 JOIN channel_v3 ON channel_v3.id = launched_equivalent_installer_for_flatpak_v3.channel_id UNION ALL launched_equivalent_installer_for_flatpak_view_v2) AS anon_1'
    )
    op.execute(
        'CREATE  VIEW "launched_existing_flatpak_view" AS SELECT anon_1.launched_existing_flatpak_v3_occured_at AS anon_1_launched_existing_flatpak_v3_occured_at, anon_1.launched_existing_flatpak_v3_os_version AS anon_1_launched_existing_flatpak_v3_os_version, anon_1.launched_existing_flatpak_v3_replacement_app_id AS anon_1_launched_existing_flatpak_v3_replacement_app_id, anon_1.launched_existing_flatpak_v3_argv AS anon_1_launched_existing_flatpak_v3_argv, anon_1.channel_v3_image_id AS anon_1_channel_v3_image_id, anon_1.channel_v3_site AS anon_1_channel_v3_site, anon_1.channel_v3_dual_boot AS anon_1_channel_v3_dual_boot, anon_1.channel_v3_live AS anon_1_channel_v3_live '
        'FROM (SELECT launched_existing_flatpak_v3.occured_at AS launched_existing_flatpak_v3_occured_at, launched_existing_flatpak_v3.os_version AS launched_existing_flatpak_v3_os_version, launched_existing_flatpak_v3.replacement_app_id AS launched_existing_flatpak_v3_replacement_app_id, launched_existing_flatpak_v3.argv AS launched_existing_flatpak_v3_argv, channel_v3.image_id AS channel_v3_image_id, channel_v3.site AS channel_v3_site, channel_v3.dual_boot AS channel_v3_dual_boot, channel_v3.live AS channel_v3_live '
        'FROM launched_existing_flatpak_v3 JOIN channel_v3 ON channel_v3.id = launched_existing_flatpak_v3.channel_id UNION ALL launched_existing_flatpak_view_v2) AS anon_1'
    )
    op.execute(
        'CREATE  VIEW "launched_installer_for_flatpak_view" AS SELECT anon_1.launched_installer_for_flatpak_v3_occured_at AS anon_1_launched_installer_for_flatpak_v3_occured_at, anon_1.launched_installer_for_flatpak_v3_os_version AS anon_1_launched_installer_for_flatpak_v3_os_version, anon_1.launched_installer_for_flatpak_v3_replacement_app_id AS anon_1_launched_installer_for_flatpak_v3_replacement_app_id, anon_1.launched_installer_for_flatpak_v3_argv AS anon_1_launched_installer_for_flatpak_v3_argv, anon_1.channel_v3_image_id AS anon_1_channel_v3_image_id, anon_1.channel_v3_site AS anon_1_channel_v3_site, anon_1.channel_v3_dual_boot AS anon_1_channel_v3_dual_boot, anon_1.channel_v3_live AS anon_1_channel_v3_live '
        'FROM (SELECT launched_installer_for_flatpak_v3.occured_at AS launched_installer_for_flatpak_v3_occured_at, launched_installer_for_flatpak_v3.os_version AS launched_installer_for_flatpak_v3_os_version, launched_installer_for_flatpak_v3.replacement_app_id AS launched_installer_for_flatpak_v3_replacement_app_id, launched_installer_for_flatpak_v3.argv AS launched_installer_for_flatpak_v3_argv, channel_v3.image_id AS channel_v3_image_id, channel_v3.site AS channel_v3_site, channel_v3.dual_boot AS channel_v3_dual_boot, channel_v3.live AS channel_v3_live '
        'FROM launched_installer_for_flatpak_v3 JOIN channel_v3 ON channel_v3.id = launched_installer_for_flatpak_v3.channel_id UNION launched_installer_for_flatpak_view_v2) AS anon_1'
    )
    op.execute(
        'CREATE  VIEW "linux_package_opened_view" AS SELECT anon_1.linux_package_opened_v3_occured_at AS anon_1_linux_package_opened_v3_occured_at, anon_1.linux_package_opened_v3_os_version AS anon_1_linux_package_opened_v3_os_version, anon_1.linux_package_opened_v3_argv AS anon_1_linux_package_opened_v3_argv, anon_1.channel_v3_image_id AS anon_1_channel_v3_image_id, anon_1.channel_v3_site AS anon_1_channel_v3_site, anon_1.channel_v3_dual_boot AS anon_1_channel_v3_dual_boot, anon_1.channel_v3_live AS anon_1_channel_v3_live '
        'FROM (SELECT linux_package_opened_v3.occured_at AS linux_package_opened_v3_occured_at, linux_package_opened_v3.os_version AS linux_package_opened_v3_os_version, linux_package_opened_v3.argv AS linux_package_opened_v3_argv, channel_v3.image_id AS channel_v3_image_id, channel_v3.site AS channel_v3_site, channel_v3.dual_boot AS channel_v3_dual_boot, channel_v3.live AS channel_v3_live '
        'FROM linux_package_opened_v3 JOIN channel_v3 ON channel_v3.id = linux_package_opened_v3.channel_id UNION linux_package_opened_view_v2) AS anon_1'
    )
    op.execute(
        'CREATE  VIEW "parental_controls_blocked_flatpak_install_view" AS SELECT anon_1.parental_controls_blocked_flatpak_install_v3_occured_at AS anon_1_parental_controls_blocked_flatpak_install_v3_occured_at, anon_1.parental_controls_blocked_flatpak_install_v3_os_version AS anon_1_parental_controls_blocked_flatpak_install_v3_os_version, anon_1.parental_controls_blocked_flatpak_install_v3_app AS anon_1_parental_controls_blocked_flatpak_install_v3_app, anon_1.channel_v3_image_id AS anon_1_channel_v3_image_id, anon_1.channel_v3_site AS anon_1_channel_v3_site, anon_1.channel_v3_dual_boot AS anon_1_channel_v3_dual_boot, anon_1.channel_v3_live AS anon_1_channel_v3_live '
        'FROM (SELECT parental_controls_blocked_flatpak_install_v3.occured_at AS parental_controls_blocked_flatpak_install_v3_occured_at, parental_controls_blocked_flatpak_install_v3.os_version AS parental_controls_blocked_flatpak_install_v3_os_version, parental_controls_blocked_flatpak_install_v3.app AS parental_controls_blocked_flatpak_install_v3_app, channel_v3.image_id AS channel_v3_image_id, channel_v3.site AS channel_v3_site, channel_v3.dual_boot AS channel_v3_dual_boot, channel_v3.live AS channel_v3_live '
        'FROM parental_controls_blocked_flatpak_install_v3 JOIN channel_v3 ON channel_v3.id = parental_controls_blocked_flatpak_install_v3.channel_id UNION parental_controls_blocked_flatpak_install_view_v2) AS anon_1'
    )
    op.execute(
        'CREATE  VIEW "parental_controls_blocked_flatpak_run_view" AS SELECT anon_1.parental_controls_blocked_flatpak_run_v3_occured_at AS anon_1_parental_controls_blocked_flatpak_run_v3_occured_at, anon_1.parental_controls_blocked_flatpak_run_v3_os_version AS anon_1_parental_controls_blocked_flatpak_run_v3_os_version, anon_1.parental_controls_blocked_flatpak_run_v3_app AS anon_1_parental_controls_blocked_flatpak_run_v3_app, anon_1.channel_v3_image_id AS anon_1_channel_v3_image_id, anon_1.channel_v3_site AS anon_1_channel_v3_site, anon_1.channel_v3_dual_boot AS anon_1_channel_v3_dual_boot, anon_1.channel_v3_live AS anon_1_channel_v3_live '
        'FROM (SELECT parental_controls_blocked_flatpak_run_v3.occured_at AS parental_controls_blocked_flatpak_run_v3_occured_at, parental_controls_blocked_flatpak_run_v3.os_version AS parental_controls_blocked_flatpak_run_v3_os_version, parental_controls_blocked_flatpak_run_v3.app AS parental_controls_blocked_flatpak_run_v3_app, channel_v3.image_id AS channel_v3_image_id, channel_v3.site AS channel_v3_site, channel_v3.dual_boot AS channel_v3_dual_boot, channel_v3.live AS channel_v3_live '
        'FROM parental_controls_blocked_flatpak_run_v3 JOIN channel_v3 ON channel_v3.id = parental_controls_blocked_flatpak_run_v3.channel_id UNION parental_controls_blocked_flatpak_run_view_v2) AS anon_1'
    )
    op.execute(
        'CREATE  VIEW "parental_controls_changed_view" AS SELECT anon_1.parental_controls_changed_v3_occured_at AS anon_1_parental_controls_changed_v3_occured_at, anon_1.parental_controls_changed_v3_os_version AS anon_1_parental_controls_changed_v3_os_version, anon_1.parental_controls_changed_v3_app_filter_is_whitelist AS anon_1_parental_controls_changed_v3_app_filter_is_whitelist, anon_1.parental_controls_changed_v3_app_filter AS anon_1_parental_controls_changed_v3_app_filter, anon_1.parental_controls_changed_v3_oars_filter AS anon_1_parental_controls_changed_v3_oars_filter, anon_1.parental_controls_changed_v3_allow_user_installation AS anon_1_parental_controls_changed_v3_allow_user_installation, anon_1.parental_controls_changed_v3_allow_system_installation AS anon_1_parental_controls_changed_v3_allow_system_installation, anon_1.parental_controls_changed_v3_is_administrator AS anon_1_parental_controls_changed_v3_is_administrator, anon_1.parental_controls_changed_v3_is_initial_setup AS anon_1_parental_controls_changed_v3_is_initial_setup, anon_1.channel_v3_image_id AS anon_1_channel_v3_image_id, anon_1.channel_v3_site AS anon_1_channel_v3_site, anon_1.channel_v3_dual_boot AS anon_1_channel_v3_dual_boot, anon_1.channel_v3_live AS anon_1_channel_v3_live '
        'FROM (SELECT parental_controls_changed_v3.occured_at AS parental_controls_changed_v3_occured_at, parental_controls_changed_v3.os_version AS parental_controls_changed_v3_os_version, parental_controls_changed_v3.app_filter_is_whitelist AS parental_controls_changed_v3_app_filter_is_whitelist, parental_controls_changed_v3.app_filter AS parental_controls_changed_v3_app_filter, parental_controls_changed_v3.oars_filter AS parental_controls_changed_v3_oars_filter, parental_controls_changed_v3.allow_user_installation AS parental_controls_changed_v3_allow_user_installation, parental_controls_changed_v3.allow_system_installation AS parental_controls_changed_v3_allow_system_installation, parental_controls_changed_v3.is_administrator AS parental_controls_changed_v3_is_administrator, parental_controls_changed_v3.is_initial_setup AS parental_controls_changed_v3_is_initial_setup, channel_v3.image_id AS channel_v3_image_id, channel_v3.site AS channel_v3_site, channel_v3.dual_boot AS channel_v3_dual_boot, channel_v3.live AS channel_v3_live '
        'FROM parental_controls_changed_v3 JOIN channel_v3 ON channel_v3.id = parental_controls_changed_v3.channel_id UNION parental_controls_changed_view_v2) AS anon_1'
    )
    op.execute(
        'CREATE  VIEW "parental_controls_enabled_view" AS SELECT anon_1.parental_controls_enabled_v3_occured_at AS anon_1_parental_controls_enabled_v3_occured_at, anon_1.parental_controls_enabled_v3_os_version AS anon_1_parental_controls_enabled_v3_os_version, anon_1.parental_controls_enabled_v3_enabled AS anon_1_parental_controls_enabled_v3_enabled, anon_1.channel_v3_image_id AS anon_1_channel_v3_image_id, anon_1.channel_v3_site AS anon_1_channel_v3_site, anon_1.channel_v3_dual_boot AS anon_1_channel_v3_dual_boot, anon_1.channel_v3_live AS anon_1_channel_v3_live '
        'FROM (SELECT parental_controls_enabled_v3.occured_at AS parental_controls_enabled_v3_occured_at, parental_controls_enabled_v3.os_version AS parental_controls_enabled_v3_os_version, parental_controls_enabled_v3.enabled AS parental_controls_enabled_v3_enabled, channel_v3.image_id AS channel_v3_image_id, channel_v3.site AS channel_v3_site, channel_v3.dual_boot AS channel_v3_dual_boot, channel_v3.live AS channel_v3_live '
        'FROM parental_controls_enabled_v3 JOIN channel_v3 ON channel_v3.id = parental_controls_enabled_v3.channel_id UNION parental_controls_enabled_view_v2) AS anon_1'
    )
    op.execute(
        'CREATE  VIEW "program_dumped_core_view" AS SELECT anon_1.program_dumped_core_v3_occured_at AS anon_1_program_dumped_core_v3_occured_at, anon_1.program_dumped_core_v3_os_version AS anon_1_program_dumped_core_v3_os_version, anon_1.program_dumped_core_v3_info AS anon_1_program_dumped_core_v3_info, anon_1.channel_v3_image_id AS anon_1_channel_v3_image_id, anon_1.channel_v3_site AS anon_1_channel_v3_site, anon_1.channel_v3_dual_boot AS anon_1_channel_v3_dual_boot, anon_1.channel_v3_live AS anon_1_channel_v3_live '
        'FROM (SELECT program_dumped_core_v3.occured_at AS program_dumped_core_v3_occured_at, program_dumped_core_v3.os_version AS program_dumped_core_v3_os_version, program_dumped_core_v3.info AS program_dumped_core_v3_info, channel_v3.image_id AS channel_v3_image_id, channel_v3.site AS channel_v3_site, channel_v3.dual_boot AS channel_v3_dual_boot, channel_v3.live AS channel_v3_live '
        'FROM program_dumped_core_v3 JOIN channel_v3 ON channel_v3.id = program_dumped_core_v3.channel_id UNION program_dumped_core_view_v2) AS anon_1'
    )
    op.execute(
        'CREATE  VIEW "updater_failure_view" AS SELECT anon_1.updater_failure_v3_occured_at AS anon_1_updater_failure_v3_occured_at, anon_1.updater_failure_v3_os_version AS anon_1_updater_failure_v3_os_version, anon_1.updater_failure_v3_component AS anon_1_updater_failure_v3_component, anon_1.updater_failure_v3_error_message AS anon_1_updater_failure_v3_error_message, anon_1.channel_v3_image_id AS anon_1_channel_v3_image_id, anon_1.channel_v3_site AS anon_1_channel_v3_site, anon_1.channel_v3_dual_boot AS anon_1_channel_v3_dual_boot, anon_1.channel_v3_live AS anon_1_channel_v3_live '
        'FROM (SELECT updater_failure_v3.occured_at AS updater_failure_v3_occured_at, updater_failure_v3.os_version AS updater_failure_v3_os_version, updater_failure_v3.component AS updater_failure_v3_component, updater_failure_v3.error_message AS updater_failure_v3_error_message, channel_v3.image_id AS channel_v3_image_id, channel_v3.site AS channel_v3_site, channel_v3.dual_boot AS channel_v3_dual_boot, channel_v3.live AS channel_v3_live '
        'FROM updater_failure_v3 JOIN channel_v3 ON channel_v3.id = updater_failure_v3.channel_id UNION updater_failure_view_v2) AS anon_1'
    )
    op.execute(
        'CREATE  VIEW "windows_app_opened_view" AS SELECT anon_1.windows_app_opened_v3_occured_at AS anon_1_windows_app_opened_v3_occured_at, anon_1.windows_app_opened_v3_os_version AS anon_1_windows_app_opened_v3_os_version, anon_1.windows_app_opened_v3_argv AS anon_1_windows_app_opened_v3_argv, anon_1.channel_v3_image_id AS anon_1_channel_v3_image_id, anon_1.channel_v3_site AS anon_1_channel_v3_site, anon_1.channel_v3_dual_boot AS anon_1_channel_v3_dual_boot, anon_1.channel_v3_live AS anon_1_channel_v3_live '
        'FROM (SELECT windows_app_opened_v3.occured_at AS windows_app_opened_v3_occured_at, windows_app_opened_v3.os_version AS windows_app_opened_v3_os_version, windows_app_opened_v3.argv AS windows_app_opened_v3_argv, channel_v3.image_id AS channel_v3_image_id, channel_v3.site AS channel_v3_site, channel_v3.dual_boot AS channel_v3_dual_boot, channel_v3.live AS channel_v3_live '
        'FROM windows_app_opened_v3 JOIN channel_v3 ON channel_v3.id = windows_app_opened_v3.channel_id UNION windows_app_opened_view_v2) AS anon_1'
    )
    op.execute(
        'CREATE  VIEW "startup_finished_view" AS SELECT anon_1.startup_finished_v3_occured_at AS anon_1_startup_finished_v3_occured_at, anon_1.startup_finished_v3_os_version AS anon_1_startup_finished_v3_os_version, anon_1.startup_finished_v3_firmware AS anon_1_startup_finished_v3_firmware, anon_1.startup_finished_v3_loader AS anon_1_startup_finished_v3_loader, anon_1.startup_finished_v3_kernel AS anon_1_startup_finished_v3_kernel, anon_1.startup_finished_v3_initrd AS anon_1_startup_finished_v3_initrd, anon_1.startup_finished_v3_userspace AS anon_1_startup_finished_v3_userspace, anon_1.startup_finished_v3_total AS anon_1_startup_finished_v3_total, anon_1.channel_v3_image_id AS anon_1_channel_v3_image_id, anon_1.channel_v3_site AS anon_1_channel_v3_site, anon_1.channel_v3_dual_boot AS anon_1_channel_v3_dual_boot, anon_1.channel_v3_live AS anon_1_channel_v3_live '
        'FROM (SELECT startup_finished_v3.occured_at AS startup_finished_v3_occured_at, startup_finished_v3.os_version AS startup_finished_v3_os_version, startup_finished_v3.firmware AS startup_finished_v3_firmware, startup_finished_v3.loader AS startup_finished_v3_loader, startup_finished_v3.kernel AS startup_finished_v3_kernel, startup_finished_v3.initrd AS startup_finished_v3_initrd, startup_finished_v3.userspace AS startup_finished_v3_userspace, startup_finished_v3.total AS startup_finished_v3_total, channel_v3.image_id AS channel_v3_image_id, channel_v3.site AS channel_v3_site, channel_v3.dual_boot AS channel_v3_dual_boot, channel_v3.live AS channel_v3_live '
        'FROM startup_finished_v3 JOIN channel_v3 ON channel_v3.id = startup_finished_v3.channel_id UNION ALL startup_finished_view_v2) AS anon_1'
    )


def downgrade():
    op.execute(
        'DROP  VIEW IF EXISTS "launched_equivalent_existing_flatpak_view"'
    )
    op.execute(
        'DROP  VIEW IF EXISTS "launched_equivalent_installer_for_flatpak_view"'
    )
    op.execute(
        'DROP  VIEW IF EXISTS "launched_existing_flatpak_view"'
    )
    op.execute(
        'DROP  VIEW IF EXISTS "launched_installer_for_flatpak_view"'
    )
    op.execute(
        'DROP  VIEW IF EXISTS "linux_package_opened_view"'
    )
    op.execute(
        'DROP  VIEW IF EXISTS "parental_controls_blocked_flatpak_install_view"'
    )
    op.execute(
        'DROP  VIEW IF EXISTS "parental_controls_blocked_flatpak_run_view"'
    )
    op.execute(
        'DROP  VIEW IF EXISTS "parental_controls_changed_view"'
    )
    op.execute(
        'DROP  VIEW IF EXISTS "parental_controls_enabled_view"'
    )
    op.execute(
        'DROP  VIEW IF EXISTS "program_dumped_core_view"'
    )
    op.execute(
        'DROP  VIEW IF EXISTS "updater_failure_view"'
    )
    op.execute(
        'DROP  VIEW IF EXISTS "windows_app_opened_view"'
    )
    op.execute(
        'DROP  VIEW IF EXISTS "startup_finished_view"'
    )
