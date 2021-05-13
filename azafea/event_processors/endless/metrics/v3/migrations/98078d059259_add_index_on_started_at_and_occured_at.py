# type: ignore

"""Add index on started_at and occured_at columns

Revision ID: 98078d059259
Revises: 29c26262aa70
Create Date: 2020-11-09 16:20:38.932519

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '98078d059259'
down_revision = '29c26262aa70'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        op.f('ix_shell_app_is_open_started_at'), 'shell_app_is_open', ['started_at'], unique=False)
    op.create_index(
        op.f('ix_user_id_logged_in_started_at'), 'user_id_logged_in', ['started_at'], unique=False)
    op.create_index(
        op.f('ix_cache_has_invalid_elements_occured_at'), 'cache_has_invalid_elements',
        ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_cache_is_corrupt_occured_at'), 'cache_is_corrupt', ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_cache_metadata_is_corrupt_occured_at'), 'cache_metadata_is_corrupt',
        ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_control_center_automatic_updates_occured_at'), 'control_center_automatic_updates',
        ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_control_center_panel_opened_occured_at'), 'control_center_panel_opened',
        ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_cpu_info_occured_at'), 'cpu_info', ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_discovery_feed_clicked_occured_at'), 'discovery_feed_clicked', ['occured_at'],
        unique=False)
    op.create_index(
        op.f('ix_discovery_feed_closed_occured_at'), 'discovery_feed_closed', ['occured_at'],
        unique=False)
    op.create_index(
        op.f('ix_discovery_feed_opened_occured_at'), 'discovery_feed_opened', ['occured_at'],
        unique=False)
    op.create_index(
        op.f('ix_disk_space_extra_occured_at'), 'disk_space_extra', ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_disk_space_sysroot_occured_at'), 'disk_space_sysroot', ['occured_at'],
        unique=False)
    op.create_index(
        op.f('ix_dual_boot_booted_occured_at'), 'dual_boot_booted', ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_endless_application_unmaximized_occured_at'), 'endless_application_unmaximized',
        ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_entered_demo_mode_occured_at'), 'entered_demo_mode', ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_hack_clubhouse_achievement_occured_at'), 'hack_clubhouse_achievement',
        ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_hack_clubhouse_achievement_points_occured_at'),
        'hack_clubhouse_achievement_points', ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_hack_clubhouse_change_page_occured_at'), 'hack_clubhouse_change_page',
        ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_hack_clubhouse_enter_pathway_occured_at'), 'hack_clubhouse_enter_pathway',
        ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_hack_clubhouse_mode_occured_at'), 'hack_clubhouse_mode', ['occured_at'],
        unique=False)
    op.create_index(
        op.f('ix_hack_clubhouse_news_quest_link_occured_at'), 'hack_clubhouse_news_quest_link',
        ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_hack_clubhouse_progress_occured_at'), 'hack_clubhouse_progress', ['occured_at'],
        unique=False)
    op.create_index(
        op.f('ix_image_version_occured_at'), 'image_version', ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_invalid_aggregate_event_occured_at'), 'invalid_aggregate_event', ['occured_at'],
        unique=False)
    op.create_index(
        op.f('ix_invalid_singular_event_occured_at'), 'invalid_singular_event', ['occured_at'],
        unique=False)
    op.create_index(
        op.f('ix_launched_equivalent_existing_flatpak_occured_at'),
        'launched_equivalent_existing_flatpak', ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_launched_equivalent_installer_for_flatpak_occured_at'),
        'launched_equivalent_installer_for_flatpak', ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_launched_existing_flatpak_occured_at'), 'launched_existing_flatpak',
        ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_launched_installer_for_flatpak_occured_at'), 'launched_installer_for_flatpak',
        ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_linux_package_opened_occured_at'), 'linux_package_opened', ['occured_at'],
        unique=False)
    op.create_index(
        op.f('ix_live_usb_booted_occured_at'), 'live_usb_booted', ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_location_occured_at'), 'location', ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_location_event_occured_at'), 'location_event', ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_missing_codec_occured_at'), 'missing_codec', ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_monitor_connected_occured_at'), 'monitor_connected', ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_monitor_disconnected_occured_at'), 'monitor_disconnected', ['occured_at'],
        unique=False)
    op.create_index(
        op.f('ix_network_id_occured_at'), 'network_id', ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_os_version_occured_at'), 'os_version', ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_parental_controls_blocked_flatpak_install_occured_at'),
        'parental_controls_blocked_flatpak_install', ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_parental_controls_blocked_flatpak_run_occured_at'),
        'parental_controls_blocked_flatpak_run', ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_parental_controls_changed_occured_at'), 'parental_controls_changed',
        ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_parental_controls_enabled_occured_at'), 'parental_controls_enabled',
        ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_program_dumped_core_occured_at'), 'program_dumped_core', ['occured_at'],
        unique=False)
    op.create_index(
        op.f('ix_ram_size_occured_at'), 'ram_size', ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_shell_app_added_to_desktop_occured_at'), 'shell_app_added_to_desktop',
        ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_shell_app_removed_from_desktop_occured_at'), 'shell_app_removed_from_desktop',
        ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_startup_finished_occured_at'), 'startup_finished', ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_underscan_enabled_occured_at'), 'underscan_enabled', ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_unknown_aggregate_event_occured_at'), 'unknown_aggregate_event', ['occured_at'],
        unique=False)
    op.create_index(
        op.f('ix_unknown_singular_event_occured_at'), 'unknown_singular_event', ['occured_at'],
        unique=False)
    op.create_index(
        op.f('ix_updater_branch_selected_occured_at'), 'updater_branch_selected', ['occured_at'],
        unique=False)
    op.create_index(
        op.f('ix_updater_failure_occured_at'), 'updater_failure', ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_uptime_occured_at'), 'uptime', ['occured_at'], unique=False)
    op.create_index(
        op.f('ix_windows_app_opened_occured_at'), 'windows_app_opened', ['occured_at'],
        unique=False)
    op.create_index(
        op.f('ix_windows_license_tables_occured_at'), 'windows_license_tables', ['occured_at'],
        unique=False)


def downgrade():
    op.drop_index(op.f('ix_user_id_logged_in_started_at'), table_name='user_id_logged_in')
    op.drop_index(op.f('ix_shell_app_is_open_started_at'), table_name='shell_app_is_open')
    op.drop_index(op.f('ix_windows_license_tables_occured_at'), table_name='windows_license_tables')
    op.drop_index(op.f('ix_windows_app_opened_occured_at'), table_name='windows_app_opened')
    op.drop_index(op.f('ix_uptime_occured_at'), table_name='uptime')
    op.drop_index(op.f('ix_updater_failure_occured_at'), table_name='updater_failure')
    op.drop_index(
        op.f('ix_updater_branch_selected_occured_at'), table_name='updater_branch_selected')
    op.drop_index(op.f('ix_unknown_singular_event_occured_at'), table_name='unknown_singular_event')
    op.drop_index(
        op.f('ix_unknown_aggregate_event_occured_at'), table_name='unknown_aggregate_event')
    op.drop_index(op.f('ix_underscan_enabled_occured_at'), table_name='underscan_enabled')
    op.drop_index(op.f('ix_startup_finished_occured_at'), table_name='startup_finished')
    op.drop_index(
        op.f('ix_shell_app_removed_from_desktop_occured_at'),
        table_name='shell_app_removed_from_desktop')
    op.drop_index(
        op.f('ix_shell_app_added_to_desktop_occured_at'), table_name='shell_app_added_to_desktop')
    op.drop_index(op.f('ix_ram_size_occured_at'), table_name='ram_size')
    op.drop_index(op.f('ix_program_dumped_core_occured_at'), table_name='program_dumped_core')
    op.drop_index(
        op.f('ix_parental_controls_enabled_occured_at'), table_name='parental_controls_enabled')
    op.drop_index(
        op.f('ix_parental_controls_changed_occured_at'), table_name='parental_controls_changed')
    op.drop_index(
        op.f('ix_parental_controls_blocked_flatpak_run_occured_at'),
        table_name='parental_controls_blocked_flatpak_run')
    op.drop_index(
        op.f('ix_parental_controls_blocked_flatpak_install_occured_at'),
        table_name='parental_controls_blocked_flatpak_install')
    op.drop_index(op.f('ix_os_version_occured_at'), table_name='os_version')
    op.drop_index(op.f('ix_network_id_occured_at'), table_name='network_id')
    op.drop_index(op.f('ix_monitor_disconnected_occured_at'), table_name='monitor_disconnected')
    op.drop_index(op.f('ix_monitor_connected_occured_at'), table_name='monitor_connected')
    op.drop_index(op.f('ix_missing_codec_occured_at'), table_name='missing_codec')
    op.drop_index(op.f('ix_location_event_occured_at'), table_name='location_event')
    op.drop_index(op.f('ix_location_occured_at'), table_name='location')
    op.drop_index(op.f('ix_live_usb_booted_occured_at'), table_name='live_usb_booted')
    op.drop_index(op.f('ix_linux_package_opened_occured_at'), table_name='linux_package_opened')
    op.drop_index(
        op.f('ix_launched_installer_for_flatpak_occured_at'),
        table_name='launched_installer_for_flatpak')
    op.drop_index(
        op.f('ix_launched_existing_flatpak_occured_at'), table_name='launched_existing_flatpak')
    op.drop_index(
        op.f('ix_launched_equivalent_installer_for_flatpak_occured_at'),
        table_name='launched_equivalent_installer_for_flatpak')
    op.drop_index(
        op.f('ix_launched_equivalent_existing_flatpak_occured_at'),
        table_name='launched_equivalent_existing_flatpak')
    op.drop_index(op.f('ix_invalid_singular_event_occured_at'), table_name='invalid_singular_event')
    op.drop_index(
        op.f('ix_invalid_aggregate_event_occured_at'), table_name='invalid_aggregate_event')
    op.drop_index(op.f('ix_image_version_occured_at'), table_name='image_version')
    op.drop_index(
        op.f('ix_hack_clubhouse_progress_occured_at'), table_name='hack_clubhouse_progress')
    op.drop_index(
        op.f('ix_hack_clubhouse_news_quest_link_occured_at'),
        table_name='hack_clubhouse_news_quest_link')
    op.drop_index(op.f('ix_hack_clubhouse_mode_occured_at'), table_name='hack_clubhouse_mode')
    op.drop_index(
        op.f('ix_hack_clubhouse_enter_pathway_occured_at'),
        table_name='hack_clubhouse_enter_pathway')
    op.drop_index(
        op.f('ix_hack_clubhouse_change_page_occured_at'), table_name='hack_clubhouse_change_page')
    op.drop_index(
        op.f('ix_hack_clubhouse_achievement_points_occured_at'),
        table_name='hack_clubhouse_achievement_points')
    op.drop_index(
        op.f('ix_hack_clubhouse_achievement_occured_at'), table_name='hack_clubhouse_achievement')
    op.drop_index(op.f('ix_entered_demo_mode_occured_at'), table_name='entered_demo_mode')
    op.drop_index(
        op.f('ix_endless_application_unmaximized_occured_at'),
        table_name='endless_application_unmaximized')
    op.drop_index(op.f('ix_dual_boot_booted_occured_at'), table_name='dual_boot_booted')
    op.drop_index(op.f('ix_disk_space_sysroot_occured_at'), table_name='disk_space_sysroot')
    op.drop_index(op.f('ix_disk_space_extra_occured_at'), table_name='disk_space_extra')
    op.drop_index(op.f('ix_discovery_feed_opened_occured_at'), table_name='discovery_feed_opened')
    op.drop_index(op.f('ix_discovery_feed_closed_occured_at'), table_name='discovery_feed_closed')
    op.drop_index(op.f('ix_discovery_feed_clicked_occured_at'), table_name='discovery_feed_clicked')
    op.drop_index(op.f('ix_cpu_info_occured_at'), table_name='cpu_info')
    op.drop_index(
        op.f('ix_control_center_panel_opened_occured_at'), table_name='control_center_panel_opened')
    op.drop_index(
        op.f('ix_control_center_automatic_updates_occured_at'),
        table_name='control_center_automatic_updates')
    op.drop_index(
        op.f('ix_cache_metadata_is_corrupt_occured_at'), table_name='cache_metadata_is_corrupt')
    op.drop_index(op.f('ix_cache_is_corrupt_occured_at'), table_name='cache_is_corrupt')
    op.drop_index(
        op.f('ix_cache_has_invalid_elements_occured_at'), table_name='cache_has_invalid_elements')
