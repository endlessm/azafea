# type: ignore

"""Initial db creation

Revision ID: 1135ef61f61e
Revises:
Create Date: 2019-12-03 14:24:34.525946

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1135ef61f61e'
down_revision = None
branch_labels = ('metrics-2',)
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'metrics_request_v2' not in tables:
        op.create_table('metrics_request_v2',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('serialized', sa.LargeBinary(), nullable=True),
                        sa.Column('sha512', sa.Unicode(), nullable=False),
                        sa.Column('received_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('absolute_timestamp', sa.BigInteger(), nullable=False),
                        sa.Column('relative_timestamp', sa.BigInteger(), nullable=False),
                        sa.Column('machine_id', sa.Unicode(length=32), nullable=False),
                        sa.Column('send_number', sa.Integer(), nullable=False),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_metrics_request_v2')),
                        sa.UniqueConstraint('sha512', name=op.f('uq_metrics_request_v2_sha512')))

    if 'cache_is_corrupt' not in tables:
        op.create_table('cache_is_corrupt',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_cache_is_corrupt_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_cache_is_corrupt')))
        op.create_index(op.f('ix_cache_is_corrupt_request_id'), 'cache_is_corrupt', ['request_id'],
                        unique=False)

    if 'cache_metadata_is_corrupt' not in tables:
        op.create_table('cache_metadata_is_corrupt',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f(
                                'fk_cache_metadata_is_corrupt_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_cache_metadata_is_corrupt')))
        op.create_index(op.f('ix_cache_metadata_is_corrupt_request_id'),
                        'cache_metadata_is_corrupt', ['request_id'], unique=False)

    if 'control_center_panel_opened' not in tables:
        op.create_table('control_center_panel_opened',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('name', sa.Unicode(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f(
                                'fk_control_center_panel_opened_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_control_center_panel_opened')))
        op.create_index(op.f('ix_control_center_panel_opened_request_id'),
                        'control_center_panel_opened', ['request_id'], unique=False)

    if 'cpu_info' not in tables:
        op.create_table('cpu_info',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('info', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_cpu_info_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_cpu_info')))
        op.create_index(op.f('ix_cpu_info_request_id'), 'cpu_info', ['request_id'], unique=False)

    if 'discovery_feed_clicked' not in tables:
        op.create_table('discovery_feed_clicked',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('info', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_discovery_feed_clicked_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_discovery_feed_clicked')))
        op.create_index(op.f('ix_discovery_feed_clicked_request_id'), 'discovery_feed_clicked',
                        ['request_id'], unique=False)

    if 'discovery_feed_closed' not in tables:
        op.create_table('discovery_feed_closed',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('info', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_discovery_feed_closed_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_discovery_feed_closed')))
        op.create_index(op.f('ix_discovery_feed_closed_request_id'), 'discovery_feed_closed',
                        ['request_id'], unique=False)

    if 'discovery_feed_opened' not in tables:
        op.create_table('discovery_feed_opened',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('info', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_discovery_feed_opened_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_discovery_feed_opened')))
        op.create_index(op.f('ix_discovery_feed_opened_request_id'), 'discovery_feed_opened',
                        ['request_id'], unique=False)

    if 'disk_space_extra' not in tables:
        op.create_table('disk_space_extra',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('total', sa.BigInteger(), nullable=False),
                        sa.Column('used', sa.BigInteger(), nullable=False),
                        sa.Column('free', sa.BigInteger(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_disk_space_extra_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_disk_space_extra')))
        op.create_index(op.f('ix_disk_space_extra_request_id'), 'disk_space_extra', ['request_id'],
                        unique=False)

    if 'disk_space_sysroot' not in tables:
        op.create_table('disk_space_sysroot',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('total', sa.BigInteger(), nullable=False),
                        sa.Column('used', sa.BigInteger(), nullable=False),
                        sa.Column('free', sa.BigInteger(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_disk_space_sysroot_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_disk_space_sysroot')))
        op.create_index(op.f('ix_disk_space_sysroot_request_id'), 'disk_space_sysroot',
                        ['request_id'], unique=False)

    if 'dual_boot_booted' not in tables:
        op.create_table('dual_boot_booted',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_dual_boot_booted_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_dual_boot_booted')))
        op.create_index(op.f('ix_dual_boot_booted_request_id'), 'dual_boot_booted', ['request_id'],
                        unique=False)

    if 'endless_application_unmaximized' not in tables:
        op.create_table('endless_application_unmaximized',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('app_id', sa.Unicode(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f(
                                'fk_endless_application_unmaximized_request_id_metrics_request_v2'
                            )),
                        sa.PrimaryKeyConstraint('id',
                                                name=op.f('pk_endless_application_unmaximized')))
        op.create_index(op.f('ix_endless_application_unmaximized_request_id'),
                        'endless_application_unmaximized', ['request_id'], unique=False)

    if 'hack_clubhouse_achievement' not in tables:
        op.create_table('hack_clubhouse_achievement',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('achievement_id', sa.Unicode(), nullable=False),
                        sa.Column('achievement_name', sa.Unicode(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f(
                                'fk_hack_clubhouse_achievement_request_id_metrics_request_v2'
                            )),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_hack_clubhouse_achievement')))
        op.create_index(op.f('ix_hack_clubhouse_achievement_request_id'),
                        'hack_clubhouse_achievement', ['request_id'], unique=False)

    if 'hack_clubhouse_achievement_points' not in tables:
        op.create_table('hack_clubhouse_achievement_points',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('skillset', sa.Unicode(), nullable=False),
                        sa.Column('points', sa.Integer(), nullable=False),
                        sa.Column('new_points', sa.Integer(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f(
                                'fk_hack_clubhouse_achievement_points_request_id_metrics_request_v2'
                            )),
                        sa.PrimaryKeyConstraint('id',
                                                name=op.f('pk_hack_clubhouse_achievement_points')))
        op.create_index(op.f('ix_hack_clubhouse_achievement_points_request_id'),
                        'hack_clubhouse_achievement_points', ['request_id'], unique=False)

    if 'hack_clubhouse_change_page' not in tables:
        op.create_table('hack_clubhouse_change_page',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('page', sa.Unicode(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f(
                                'fk_hack_clubhouse_change_page_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_hack_clubhouse_change_page')))
        op.create_index(op.f('ix_hack_clubhouse_change_page_request_id'),
                        'hack_clubhouse_change_page', ['request_id'], unique=False)

    if 'hack_clubhouse_enter_pathway' not in tables:
        op.create_table('hack_clubhouse_enter_pathway',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('pathway', sa.Unicode(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f(
                                'fk_hack_clubhouse_enter_pathway_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_hack_clubhouse_enter_pathway')))
        op.create_index(op.f('ix_hack_clubhouse_enter_pathway_request_id'),
                        'hack_clubhouse_enter_pathway', ['request_id'], unique=False)

    if 'hack_clubhouse_mode' not in tables:
        op.create_table('hack_clubhouse_mode',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('active', sa.Boolean(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_hack_clubhouse_mode_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_hack_clubhouse_mode')))
        op.create_index(op.f('ix_hack_clubhouse_mode_request_id'), 'hack_clubhouse_mode',
                        ['request_id'], unique=False)

    if 'hack_clubhouse_progress' not in tables:
        op.create_table('hack_clubhouse_progress',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('complete', sa.Boolean(), nullable=False),
                        sa.Column('quest', sa.Unicode(), nullable=False),
                        sa.Column('pathways', sa.ARRAY(sa.Unicode(), dimensions=1), nullable=False),
                        sa.Column('progress', sa.Numeric(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_hack_clubhouse_progress_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_hack_clubhouse_progress')))
        op.create_index(op.f('ix_hack_clubhouse_progress_request_id'), 'hack_clubhouse_progress',
                        ['request_id'], unique=False)

    if 'image_version' not in tables:
        op.create_table('image_version',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('image_id', sa.Unicode(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_image_version_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_image_version')))
        op.create_index(op.f('ix_image_version_request_id'), 'image_version', ['request_id'],
                        unique=False)

    if 'invalid_aggregate_event' not in tables:
        op.create_table('invalid_aggregate_event',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
                        sa.Column('payload_data', sa.LargeBinary(), nullable=False),
                        sa.Column('error', sa.Unicode(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('count', sa.BigInteger(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_invalid_aggregate_event_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_invalid_aggregate_event')))
        op.create_index(op.f('ix_invalid_aggregate_event_request_id'), 'invalid_aggregate_event',
                        ['request_id'], unique=False)

    if 'invalid_sequence' not in tables:
        op.create_table('invalid_sequence',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
                        sa.Column('payload_data', sa.LargeBinary(), nullable=False),
                        sa.Column('error', sa.Unicode(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_invalid_sequence_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_invalid_sequence')))
        op.create_index(op.f('ix_invalid_sequence_request_id'), 'invalid_sequence', ['request_id'],
                        unique=False)

    if 'invalid_singular_event' not in tables:
        op.create_table('invalid_singular_event',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
                        sa.Column('payload_data', sa.LargeBinary(), nullable=False),
                        sa.Column('error', sa.Unicode(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_invalid_singular_event_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_invalid_singular_event')))
        op.create_index(op.f('ix_invalid_singular_event_request_id'), 'invalid_singular_event',
                        ['request_id'], unique=False)

    if 'launched_equivalent_existing_flatpak' not in tables:
        op.create_table('launched_equivalent_existing_flatpak',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('replacement_app_id', sa.Unicode(), nullable=False),
                        sa.Column('argv', sa.ARRAY(sa.Unicode(), dimensions=1), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_launched_equivalent_existing_flatpak_request_id_metrics_request_v2')),  # noqa: E501
                        sa.PrimaryKeyConstraint(
                            'id', name=op.f('pk_launched_equivalent_existing_flatpak')))
        op.create_index(op.f('ix_launched_equivalent_existing_flatpak_request_id'),
                        'launched_equivalent_existing_flatpak', ['request_id'], unique=False)

    if 'launched_equivalent_installer_for_flatpak' not in tables:
        op.create_table('launched_equivalent_installer_for_flatpak',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('replacement_app_id', sa.Unicode(), nullable=False),
                        sa.Column('argv', sa.ARRAY(sa.Unicode(), dimensions=1), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_launched_equivalent_installer_for_flatpak_request_id_metrics_request_v2')),  # noqa: E501
                        sa.PrimaryKeyConstraint(
                            'id', name=op.f('pk_launched_equivalent_installer_for_flatpak')))
        op.create_index(op.f('ix_launched_equivalent_installer_for_flatpak_request_id'),
                        'launched_equivalent_installer_for_flatpak', ['request_id'], unique=False)

    if 'launched_existing_flatpak' not in tables:
        op.create_table('launched_existing_flatpak',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('replacement_app_id', sa.Unicode(), nullable=False),
                        sa.Column('argv', sa.ARRAY(sa.Unicode(), dimensions=1), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f(
                                'fk_launched_existing_flatpak_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_launched_existing_flatpak')))
        op.create_index(op.f('ix_launched_existing_flatpak_request_id'),
                        'launched_existing_flatpak', ['request_id'], unique=False)

    if 'launched_installer_for_flatpak' not in tables:
        op.create_table('launched_installer_for_flatpak',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('replacement_app_id', sa.Unicode(), nullable=False),
                        sa.Column('argv', sa.ARRAY(sa.Unicode(), dimensions=1), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f(
                                'fk_launched_installer_for_flatpak_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id',
                                                name=op.f('pk_launched_installer_for_flatpak')))
        op.create_index(op.f('ix_launched_installer_for_flatpak_request_id'),
                        'launched_installer_for_flatpak', ['request_id'], unique=False)

    if 'linux_package_opened' not in tables:
        op.create_table('linux_package_opened',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('argv', sa.ARRAY(sa.Unicode(), dimensions=1), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_linux_package_opened_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_linux_package_opened')))
        op.create_index(op.f('ix_linux_package_opened_request_id'), 'linux_package_opened',
                        ['request_id'], unique=False)

    if 'live_usb_booted' not in tables:
        op.create_table('live_usb_booted',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_live_usb_booted_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_live_usb_booted')))
        op.create_index(op.f('ix_live_usb_booted_request_id'), 'live_usb_booted', ['request_id'],
                        unique=False)

    if 'location' not in tables:
        op.create_table('location',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('latitude', postgresql.DOUBLE_PRECISION(), nullable=False),
                        sa.Column('longitude', postgresql.DOUBLE_PRECISION(), nullable=False),
                        sa.Column('altitude', postgresql.DOUBLE_PRECISION(), nullable=True),
                        sa.Column('accuracy', postgresql.DOUBLE_PRECISION(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_location_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_location')))
        op.create_index(op.f('ix_location_request_id'), 'location', ['request_id'], unique=False)

    if 'location_event' not in tables:
        op.create_table('location_event',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('info', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_location_event_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_location_event')))
        op.create_index(op.f('ix_location_event_request_id'), 'location_event', ['request_id'],
                        unique=False)

    if 'missing_codec' not in tables:
        op.create_table('missing_codec',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('gstreamer_version', sa.Unicode(), nullable=False),
                        sa.Column('app_name', sa.Unicode(), nullable=False),
                        sa.Column('type', sa.Unicode(), nullable=False),
                        sa.Column('name', sa.Unicode(), nullable=False),
                        sa.Column('extra_info', postgresql.JSONB(astext_type=sa.Text()),
                                  nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_missing_codec_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_missing_codec')))
        op.create_index(op.f('ix_missing_codec_request_id'), 'missing_codec', ['request_id'],
                        unique=False)

    if 'monitor_connected' not in tables:
        op.create_table('monitor_connected',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('display_name', sa.Unicode(), nullable=False),
                        sa.Column('display_vendor', sa.Unicode(), nullable=False),
                        sa.Column('display_product', sa.Unicode(), nullable=False),
                        sa.Column('display_width', sa.Integer(), nullable=False),
                        sa.Column('display_height', sa.Integer(), nullable=False),
                        sa.Column('edid', sa.LargeBinary(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_monitor_connected_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_monitor_connected')))
        op.create_index(op.f('ix_monitor_connected_request_id'), 'monitor_connected',
                        ['request_id'], unique=False)

    if 'monitor_disconnected' not in tables:
        op.create_table('monitor_disconnected',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('display_name', sa.Unicode(), nullable=False),
                        sa.Column('display_vendor', sa.Unicode(), nullable=False),
                        sa.Column('display_product', sa.Unicode(), nullable=False),
                        sa.Column('display_width', sa.Integer(), nullable=False),
                        sa.Column('display_height', sa.Integer(), nullable=False),
                        sa.Column('edid', sa.LargeBinary(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_monitor_disconnected_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_monitor_disconnected')))
        op.create_index(op.f('ix_monitor_disconnected_request_id'), 'monitor_disconnected',
                        ['request_id'], unique=False)

    if 'network_id' not in tables:
        op.create_table('network_id',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('network_id', sa.BigInteger(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_network_id_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_network_id')))
        op.create_index(op.f('ix_network_id_request_id'), 'network_id', ['request_id'],
                        unique=False)

    if 'os_version' not in tables:
        op.create_table('os_version',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('name', sa.Unicode(), nullable=False),
                        sa.Column('version', sa.Unicode(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_os_version_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_os_version')))
        op.create_index(op.f('ix_os_version_request_id'), 'os_version', ['request_id'],
                        unique=False)

    if 'program_dumped_core' not in tables:
        op.create_table('program_dumped_core',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('info', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_program_dumped_core_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_program_dumped_core')))
        op.create_index(op.f('ix_program_dumped_core_request_id'), 'program_dumped_core',
                        ['request_id'], unique=False)

    if 'ram_size' not in tables:
        op.create_table('ram_size',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('total', sa.BigInteger(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_ram_size_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_ram_size')))
        op.create_index(op.f('ix_ram_size_request_id'), 'ram_size', ['request_id'], unique=False)

    if 'shell_app_added_to_desktop' not in tables:
        op.create_table('shell_app_added_to_desktop',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('app_id', sa.Unicode(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f(
                                'fk_shell_app_added_to_desktop_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_shell_app_added_to_desktop')))
        op.create_index(op.f('ix_shell_app_added_to_desktop_request_id'),
                        'shell_app_added_to_desktop', ['request_id'], unique=False)

    if 'shell_app_is_open' not in tables:
        op.create_table('shell_app_is_open',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('stopped_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('app_id', sa.Unicode(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_shell_app_is_open_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_shell_app_is_open')))
        op.create_index(op.f('ix_shell_app_is_open_request_id'), 'shell_app_is_open',
                        ['request_id'], unique=False)

    if 'shell_app_removed_from_desktop' not in tables:
        op.create_table('shell_app_removed_from_desktop',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('app_id', sa.Unicode(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f(
                                'fk_shell_app_removed_from_desktop_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id',
                                                name=op.f('pk_shell_app_removed_from_desktop')))
        op.create_index(op.f('ix_shell_app_removed_from_desktop_request_id'),
                        'shell_app_removed_from_desktop', ['request_id'], unique=False)

    if 'unknown_aggregate_event' not in tables:
        op.create_table('unknown_aggregate_event',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
                        sa.Column('payload_data', sa.LargeBinary(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('count', sa.BigInteger(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_unknown_aggregate_event_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_unknown_aggregate_event')))
        op.create_index(op.f('ix_unknown_aggregate_event_request_id'), 'unknown_aggregate_event',
                        ['request_id'], unique=False)

    if 'unknown_sequence' not in tables:
        op.create_table('unknown_sequence',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
                        sa.Column('payload_data', sa.LargeBinary(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_unknown_sequence_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_unknown_sequence')))
        op.create_index(op.f('ix_unknown_sequence_request_id'), 'unknown_sequence', ['request_id'],
                        unique=False)

    if 'unknown_singular_event' not in tables:
        op.create_table('unknown_singular_event',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
                        sa.Column('payload_data', sa.LargeBinary(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_unknown_singular_event_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_unknown_singular_event')))
        op.create_index(op.f('ix_unknown_singular_event_request_id'), 'unknown_singular_event',
                        ['request_id'], unique=False)

    if 'updater_branch_selected' not in tables:
        op.create_table('updater_branch_selected',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('hardware_vendor', sa.Unicode(), nullable=False),
                        sa.Column('hardware_product', sa.Unicode(), nullable=False),
                        sa.Column('ostree_branch', sa.Unicode(), nullable=False),
                        sa.Column('on_hold', sa.Boolean(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_updater_branch_selected_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_updater_branch_selected')))
        op.create_index(op.f('ix_updater_branch_selected_request_id'), 'updater_branch_selected',
                        ['request_id'], unique=False)

    if 'uptime' not in tables:
        op.create_table('uptime',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('accumulated_uptime', sa.BigInteger(), nullable=False),
                        sa.Column('number_of_boots', sa.BigInteger(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_uptime_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_uptime')))
        op.create_index(op.f('ix_uptime_request_id'), 'uptime', ['request_id'], unique=False)

    if 'user_id_logged_in' not in tables:
        op.create_table('user_id_logged_in',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('stopped_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('logged_in_user_id', sa.BigInteger(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_user_id_logged_in_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_user_id_logged_in')))
        op.create_index(op.f('ix_user_id_logged_in_request_id'), 'user_id_logged_in',
                        ['request_id'], unique=False)

    if 'windows_app_opened' not in tables:
        op.create_table('windows_app_opened',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('argv', sa.ARRAY(sa.Unicode(), dimensions=1), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_windows_app_opened_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_windows_app_opened')))
        op.create_index(op.f('ix_windows_app_opened_request_id'), 'windows_app_opened',
                        ['request_id'], unique=False)

    if 'windows_license_tables' not in tables:
        op.create_table('windows_license_tables',
                        sa.Column('id', sa.Integer(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('occured_at', sa.DateTime(timezone=True), nullable=False),
                        sa.Column('tables', sa.BigInteger(), nullable=False),
                        sa.Column('request_id', sa.Integer(), nullable=True),
                        sa.ForeignKeyConstraint(
                            ['request_id'], ['metrics_request_v2.id'],
                            name=op.f('fk_windows_license_tables_request_id_metrics_request_v2')),
                        sa.PrimaryKeyConstraint('id', name=op.f('pk_windows_license_tables')))
        op.create_index(op.f('ix_windows_license_tables_request_id'), 'windows_license_tables',
                        ['request_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_windows_license_tables_request_id'), table_name='windows_license_tables')
    op.drop_table('windows_license_tables')
    op.drop_index(op.f('ix_windows_app_opened_request_id'), table_name='windows_app_opened')
    op.drop_table('windows_app_opened')
    op.drop_index(op.f('ix_user_id_logged_in_request_id'), table_name='user_id_logged_in')
    op.drop_table('user_id_logged_in')
    op.drop_index(op.f('ix_uptime_request_id'), table_name='uptime')
    op.drop_table('uptime')
    op.drop_index(op.f('ix_updater_branch_selected_request_id'),
                  table_name='updater_branch_selected')
    op.drop_table('updater_branch_selected')
    op.drop_index(op.f('ix_unknown_singular_event_request_id'), table_name='unknown_singular_event')
    op.drop_table('unknown_singular_event')
    op.drop_index(op.f('ix_unknown_sequence_request_id'), table_name='unknown_sequence')
    op.drop_table('unknown_sequence')
    op.drop_index(op.f('ix_unknown_aggregate_event_request_id'),
                  table_name='unknown_aggregate_event')
    op.drop_table('unknown_aggregate_event')
    op.drop_index(op.f('ix_shell_app_removed_from_desktop_request_id'),
                  table_name='shell_app_removed_from_desktop')
    op.drop_table('shell_app_removed_from_desktop')
    op.drop_index(op.f('ix_shell_app_is_open_request_id'), table_name='shell_app_is_open')
    op.drop_table('shell_app_is_open')
    op.drop_index(op.f('ix_shell_app_added_to_desktop_request_id'),
                  table_name='shell_app_added_to_desktop')
    op.drop_table('shell_app_added_to_desktop')
    op.drop_index(op.f('ix_ram_size_request_id'), table_name='ram_size')
    op.drop_table('ram_size')
    op.drop_index(op.f('ix_program_dumped_core_request_id'), table_name='program_dumped_core')
    op.drop_table('program_dumped_core')
    op.drop_index(op.f('ix_os_version_request_id'), table_name='os_version')
    op.drop_table('os_version')
    op.drop_index(op.f('ix_network_id_request_id'), table_name='network_id')
    op.drop_table('network_id')
    op.drop_index(op.f('ix_monitor_disconnected_request_id'), table_name='monitor_disconnected')
    op.drop_table('monitor_disconnected')
    op.drop_index(op.f('ix_monitor_connected_request_id'), table_name='monitor_connected')
    op.drop_table('monitor_connected')
    op.drop_index(op.f('ix_missing_codec_request_id'), table_name='missing_codec')
    op.drop_table('missing_codec')
    op.drop_index(op.f('ix_location_event_request_id'), table_name='location_event')
    op.drop_table('location_event')
    op.drop_index(op.f('ix_location_request_id'), table_name='location')
    op.drop_table('location')
    op.drop_index(op.f('ix_live_usb_booted_request_id'), table_name='live_usb_booted')
    op.drop_table('live_usb_booted')
    op.drop_index(op.f('ix_linux_package_opened_request_id'), table_name='linux_package_opened')
    op.drop_table('linux_package_opened')
    op.drop_index(op.f('ix_launched_installer_for_flatpak_request_id'),
                  table_name='launched_installer_for_flatpak')
    op.drop_table('launched_installer_for_flatpak')
    op.drop_index(op.f('ix_launched_existing_flatpak_request_id'),
                  table_name='launched_existing_flatpak')
    op.drop_table('launched_existing_flatpak')
    op.drop_index(op.f('ix_launched_equivalent_installer_for_flatpak_request_id'),
                  table_name='launched_equivalent_installer_for_flatpak')
    op.drop_table('launched_equivalent_installer_for_flatpak')
    op.drop_index(op.f('ix_launched_equivalent_existing_flatpak_request_id'),
                  table_name='launched_equivalent_existing_flatpak')
    op.drop_table('launched_equivalent_existing_flatpak')
    op.drop_index(op.f('ix_invalid_singular_event_request_id'), table_name='invalid_singular_event')
    op.drop_table('invalid_singular_event')
    op.drop_index(op.f('ix_invalid_sequence_request_id'), table_name='invalid_sequence')
    op.drop_table('invalid_sequence')
    op.drop_index(op.f('ix_invalid_aggregate_event_request_id'),
                  table_name='invalid_aggregate_event')
    op.drop_table('invalid_aggregate_event')
    op.drop_index(op.f('ix_image_version_request_id'), table_name='image_version')
    op.drop_table('image_version')
    op.drop_index(op.f('ix_hack_clubhouse_progress_request_id'),
                  table_name='hack_clubhouse_progress')
    op.drop_table('hack_clubhouse_progress')
    op.drop_index(op.f('ix_hack_clubhouse_mode_request_id'), table_name='hack_clubhouse_mode')
    op.drop_table('hack_clubhouse_mode')
    op.drop_index(op.f('ix_hack_clubhouse_enter_pathway_request_id'),
                  table_name='hack_clubhouse_enter_pathway')
    op.drop_table('hack_clubhouse_enter_pathway')
    op.drop_index(op.f('ix_hack_clubhouse_change_page_request_id'),
                  table_name='hack_clubhouse_change_page')
    op.drop_table('hack_clubhouse_change_page')
    op.drop_index(op.f('ix_hack_clubhouse_achievement_points_request_id'),
                  table_name='hack_clubhouse_achievement_points')
    op.drop_table('hack_clubhouse_achievement_points')
    op.drop_index(op.f('ix_hack_clubhouse_achievement_request_id'),
                  table_name='hack_clubhouse_achievement')
    op.drop_table('hack_clubhouse_achievement')
    op.drop_index(op.f('ix_endless_application_unmaximized_request_id'),
                  table_name='endless_application_unmaximized')
    op.drop_table('endless_application_unmaximized')
    op.drop_index(op.f('ix_dual_boot_booted_request_id'), table_name='dual_boot_booted')
    op.drop_table('dual_boot_booted')
    op.drop_index(op.f('ix_disk_space_sysroot_request_id'), table_name='disk_space_sysroot')
    op.drop_table('disk_space_sysroot')
    op.drop_index(op.f('ix_disk_space_extra_request_id'), table_name='disk_space_extra')
    op.drop_table('disk_space_extra')
    op.drop_index(op.f('ix_discovery_feed_opened_request_id'), table_name='discovery_feed_opened')
    op.drop_table('discovery_feed_opened')
    op.drop_index(op.f('ix_discovery_feed_closed_request_id'), table_name='discovery_feed_closed')
    op.drop_table('discovery_feed_closed')
    op.drop_index(op.f('ix_discovery_feed_clicked_request_id'), table_name='discovery_feed_clicked')
    op.drop_table('discovery_feed_clicked')
    op.drop_index(op.f('ix_cpu_info_request_id'), table_name='cpu_info')
    op.drop_table('cpu_info')
    op.drop_index(op.f('ix_control_center_panel_opened_request_id'),
                  table_name='control_center_panel_opened')
    op.drop_table('control_center_panel_opened')
    op.drop_index(op.f('ix_cache_metadata_is_corrupt_request_id'),
                  table_name='cache_metadata_is_corrupt')
    op.drop_table('cache_metadata_is_corrupt')
    op.drop_index(op.f('ix_cache_is_corrupt_request_id'), table_name='cache_is_corrupt')
    op.drop_table('cache_is_corrupt')
    op.drop_table('metrics_request_v2')
    op.drop_table('alembic_version_metrics_v2')
