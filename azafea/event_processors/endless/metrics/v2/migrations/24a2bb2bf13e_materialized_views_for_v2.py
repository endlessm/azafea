# type: ignore

"""Materialized views for metrics v2 events

Revision ID: 24a2bb2bf13e
Revises: 8eb67a73775b
Create Date: 2021-07-15 16:01:40.617855

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '24a2bb2bf13e'
down_revision = '8eb67a73775b'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "CREATE MATERIALIZED VIEW launched_equivalent_existing_flatpak_view_v2 "
        "(occured_at, os_version, replacement_app_id, argv, image_id, site, dual_boot, live) AS "
        "SELECT DISTINCT ON (l.id) l.occured_at, os.version AS os_version, replacement_app_id, "
        "argv, image_id, location, dualboot, live "
        "FROM launched_equivalent_existing_flatpak l "
        "LEFT OUTER JOIN metrics_request_v2 mr ON l.request_id=mr.id "
        "LEFT OUTER JOIN metrics_machine mm USING (machine_id) "
        "LEFT OUTER JOIN os_version os USING (request_id) "
        "WHERE not mm.demo"
    )

    op.execute(
        "CREATE MATERIALIZED VIEW launched_equivalent_installer_for_flatpak_view_v2 "
        "(occured_at, os_version, replacement_app_id, argv, image_id, site, dual_boot, live) AS "
        "SELECT DISTINCT ON (l.id) l.occured_at, os.version AS os_version, replacement_app_id, "
        "argv, image_id, location, dualboot, live "
        "FROM launched_equivalent_installer_for_flatpak l "
        "LEFT OUTER JOIN metrics_request_v2 mr ON l.request_id=mr.id "
        "LEFT OUTER JOIN metrics_machine mm USING (machine_id) "
        "LEFT OUTER JOIN os_version os USING (request_id) "
        "WHERE not mm.demo"
    )

    op.execute(
        "CREATE MATERIALIZED VIEW launched_existing_flatpak_view_v2 "
        "(occured_at, os_version, replacement_app_id, argv, image_id, site, dual_boot, live) AS "
        "SELECT DISTINCT ON (l.id) l.occured_at, os.version AS os_version, replacement_app_id, "
        "argv, image_id, location, dualboot, live "
        "FROM launched_existing_flatpak l "
        "LEFT OUTER JOIN metrics_request_v2 mr ON l.request_id=mr.id "
        "LEFT OUTER JOIN metrics_machine mm USING (machine_id) "
        "LEFT OUTER JOIN os_version os USING (request_id) "
        "WHERE not mm.demo"
    )

    op.execute(
        "CREATE MATERIALIZED VIEW launched_installer_for_flatpak_view_v2 "
        "(occured_at, os_version, replacement_app_id, argv, image_id, site, dual_boot, live) AS "
        "SELECT DISTINCT ON (l.id) l.occured_at, os.version AS os_version, replacement_app_id, "
        "argv, image_id, location, dualboot, live "
        "FROM launched_installer_for_flatpak l "
        "LEFT OUTER JOIN metrics_request_v2 mr ON l.request_id=mr.id "
        "LEFT OUTER JOIN metrics_machine mm USING (machine_id) "
        "LEFT OUTER JOIN os_version os USING (request_id) "
        "WHERE not mm.demo"
    )

    op.execute(
        "CREATE MATERIALIZED VIEW linux_package_opened_view_v2 "
        "(occured_at, os_version, argv, image_id, site, dual_boot, live) AS "
        "SELECT DISTINCT ON (l.id) l.occured_at, os.version AS os_version, "
        "argv, image_id, location, dualboot, live "
        "FROM linux_package_opened l "
        "LEFT OUTER JOIN metrics_request_v2 mr ON l.request_id=mr.id "
        "LEFT OUTER JOIN metrics_machine mm USING (machine_id) "
        "LEFT OUTER JOIN os_version os USING (request_id) "
        "WHERE not mm.demo"
    )

    op.execute(
        "CREATE MATERIALIZED VIEW parental_controls_blocked_flatpak_install_view_v2 "
        "(occured_at, os_version, app, image_id, site, dual_boot, live) AS "
        "SELECT DISTINCT ON (l.id) l.occured_at, os.version AS os_version, "
        "app, image_id, location, dualboot, live "
        "FROM parental_controls_blocked_flatpak_install l "
        "LEFT OUTER JOIN metrics_request_v2 mr ON l.request_id=mr.id "
        "LEFT OUTER JOIN metrics_machine mm USING (machine_id) "
        "LEFT OUTER JOIN os_version os USING (request_id) "
        "WHERE not mm.demo"
    )

    op.execute(
        "CREATE MATERIALIZED VIEW parental_controls_blocked_flatpak_run_view_v2 "
        "(occured_at, os_version, app, image_id, site, dual_boot, live) AS "
        "SELECT DISTINCT ON (l.id) l.occured_at, os.version AS os_version, "
        "app, image_id, location, dualboot, live "
        "FROM parental_controls_blocked_flatpak_run l "
        "LEFT OUTER JOIN metrics_request_v2 mr ON l.request_id=mr.id "
        "LEFT OUTER JOIN metrics_machine mm USING (machine_id) "
        "LEFT OUTER JOIN os_version os USING (request_id) "
        "WHERE not mm.demo"
    )

    op.execute(
        "CREATE MATERIALIZED VIEW parental_controls_changed_view_v2 "
        "(occured_at, os_version, app_filter_is_whitelist, app_filter, oars_filter, "
        "allow_user_installation, allow_system_installation, is_administrator, "
        "is_initial_setup, image_id, site, dual_boot, live) AS "
        "SELECT DISTINCT ON (l.id) l.occured_at, os.version AS os_version, "
        "app_filter_is_whitelist, app_filter, oars_filter, allow_user_installation, "
        "allow_system_installation, is_administrator, is_initial_setup, image_id, "
        "location, dualboot, live "
        "FROM parental_controls_changed l "
        "LEFT OUTER JOIN metrics_request_v2 mr ON l.request_id=mr.id "
        "LEFT OUTER JOIN metrics_machine mm USING (machine_id) "
        "LEFT OUTER JOIN os_version os USING (request_id) "
        "WHERE not mm.demo"
    )

    op.execute(
        "CREATE MATERIALIZED VIEW parental_controls_enabled_view_v2 "
        "(occured_at, os_version, enabled, image_id, site, dual_boot, live) AS "
        "SELECT DISTINCT ON (l.id) l.occured_at, os.version AS os_version, "
        "enabled, image_id, location, dualboot, live "
        "FROM parental_controls_enabled l "
        "LEFT OUTER JOIN metrics_request_v2 mr ON l.request_id=mr.id "
        "LEFT OUTER JOIN metrics_machine mm USING (machine_id) "
        "LEFT OUTER JOIN os_version os USING (request_id) "
        "WHERE not mm.demo"
    )

    op.execute(
        "CREATE MATERIALIZED VIEW program_dumped_core_view_v2 "
        "(occured_at, os_version, info, image_id, site, dual_boot, live) AS "
        "SELECT DISTINCT ON (l.id) l.occured_at, os.version AS os_version, "
        "info, image_id, location, dualboot, live "
        "FROM program_dumped_core l "
        "LEFT OUTER JOIN metrics_request_v2 mr ON l.request_id=mr.id "
        "LEFT OUTER JOIN metrics_machine mm USING (machine_id) "
        "LEFT OUTER JOIN os_version os USING (request_id) "
        "WHERE not mm.demo"
    )

    op.execute(
        "CREATE MATERIALIZED VIEW updater_failure_view_v2 "
        "(occured_at, os_version, component, error_message, image_id, site, dual_boot, live) AS "
        "SELECT DISTINCT ON (l.id) l.occured_at, os.version AS os_version, "
        "component, error_message, image_id, location, dualboot, live "
        "FROM updater_failure l "
        "LEFT OUTER JOIN metrics_request_v2 mr ON l.request_id=mr.id "
        "LEFT OUTER JOIN metrics_machine mm USING (machine_id) "
        "LEFT OUTER JOIN os_version os USING (request_id) "
        "WHERE not mm.demo"
    )

    op.execute(
        "CREATE MATERIALIZED VIEW windows_app_opened_view_v2 "
        "(occured_at, os_version, argv, image_id, site, dual_boot, live) AS "
        "SELECT DISTINCT ON (l.id) l.occured_at, os.version AS os_version, "
        "argv, image_id, location, dualboot, live "
        "FROM windows_app_opened l "
        "LEFT OUTER JOIN metrics_request_v2 mr ON l.request_id=mr.id "
        "LEFT OUTER JOIN metrics_machine mm USING (machine_id) "
        "LEFT OUTER JOIN os_version os USING (request_id) "
        "WHERE not mm.demo"
    )

    op.execute(
        "CREATE MATERIALIZED VIEW startup_finished_view_v2 "
        "(occured_at, os_version, firmware, loader, kernel, initrd, userspace, total, "
        "image_id, site, dual_boot, live) AS "
        "SELECT DISTINCT ON (l.id) l.occured_at, os.version AS os_version, "
        "firmware, loader, kernel, initrd, userspace, total, image_id, location, dualboot, live "
        "FROM startup_finished l "
        "LEFT OUTER JOIN metrics_request_v2 mr ON l.request_id=mr.id "
        "LEFT OUTER JOIN metrics_machine mm USING (machine_id) "
        "LEFT OUTER JOIN os_version os USING (request_id) "
        "WHERE not mm.demo"
    )


def downgrade():
    op.execute("DROP MATERIALIZED VIEW launched_equivalent_existing_flatpak_view_v2")
    op.execute("DROP MATERIALIZED VIEW launched_equivalent_installer_for_flatpak_view_v2")
    op.execute("DROP MATERIALIZED VIEW launched_existing_flatpak_view_v2")
    op.execute("DROP MATERIALIZED VIEW launched_installer_for_flatpak_view_v2")
    op.execute("DROP MATERIALIZED VIEW linux_package_opened_view_v2")
    op.execute("DROP MATERIALIZED VIEW parental_controls_blocked_flatpak_install_view_v2")
    op.execute("DROP MATERIALIZED VIEW parental_controls_blocked_flatpak_run_view_v2")
    op.execute("DROP MATERIALIZED VIEW parental_controls_changed_view_v2")
    op.execute("DROP MATERIALIZED VIEW parental_controls_enabled_view_v2")
    op.execute("DROP MATERIALIZED VIEW program_dumped_core_view_v2")
    op.execute("DROP MATERIALIZED VIEW updater_failure_view_v2")
    op.execute("DROP MATERIALIZED VIEW windows_app_opened_view_v2")
    op.execute("DROP MATERIALIZED VIEW startup_finished_view_v2")
