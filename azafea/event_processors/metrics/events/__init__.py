# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from typing import Any, Dict

from gi.repository import GLib

from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION, JSONB
from sqlalchemy.event import listens_for
from sqlalchemy.schema import Column
from sqlalchemy.types import ARRAY, BigInteger, Boolean, Integer, LargeBinary, Numeric, Unicode

from azafea.model import DbSession
from azafea.vendors import normalize_vendor
from ..machine import insert_machine
from ..utils import get_asv_dict, get_bytes, get_child_values, get_strings
from ._base import (  # noqa: F401
    SequenceEvent,
    SingularEvent,
    # Reexport some symbols
    InvalidAggregateEvent,
    InvalidSequence,
    InvalidSingularEvent,
    UnknownAggregateEvent,
    UnknownSequence,
    UnknownSingularEvent,
    new_aggregate_event,
    new_sequence_event,
    new_singular_event,
    replay_invalid_aggregate_events,
    replay_invalid_sequences,
    replay_invalid_singular_events,
    replay_unknown_aggregate_events,
    replay_unknown_sequences,
    replay_unknown_singular_events,
    aggregate_event_is_known,
    sequence_is_known,
    singular_event_is_known,
)


# -- Singular events ----------------------------------------------------------

class CacheIsCorrupt(SingularEvent):
    __tablename__ = 'cache_is_corrupt'
    __event_uuid__ = 'd84b9a19-9353-73eb-70bf-f91a584abcbd'
    __payload_type__ = None


class CacheMetadataIsCorrupt(SingularEvent):
    __tablename__ = 'cache_metadata_is_corrupt'
    __event_uuid__ = 'f0e8a206-3bc2-405e-90d0-ef6fe6dd7edc'
    __payload_type__ = None


class ControlCenterPanelOpened(SingularEvent):
    __tablename__ = 'control_center_panel_opened'
    __event_uuid__ = '3c5d59d2-6c3f-474b-95f4-ac6fcc192655'
    __payload_type__ = 's'

    name = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'name': payload.get_string()}


class CPUInfo(SingularEvent):
    __tablename__ = 'cpu_info'
    __event_uuid__ = '4a75488a-0d9a-4c38-8556-148f500edaf0'
    __payload_type__ = 'a(sqd)'

    info = Column(JSONB, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        info = []

        for i in range(payload.n_children()):
            item = payload.get_child_value(i)
            info.append({
                'model': item.get_child_value(0).get_string(),
                'cores': item.get_child_value(1).get_uint16(),
                'max_frequency': item.get_child_value(2).get_double(),
            })

        return {'info': info}


class DiscoveryFeedClicked(SingularEvent):
    __tablename__ = 'discovery_feed_clicked'
    __event_uuid__ = 'f2f31a64-2193-42b5-ae39-ca0b4d1f0691'
    __payload_type__ = 'a{ss}'

    info = Column(JSONB, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'info': get_asv_dict(payload)}


class DiscoveryFeedClosed(SingularEvent):
    __tablename__ = 'discovery_feed_closed'
    __event_uuid__ = 'e7932cbd-7c20-49eb-94e9-4bf075e0c0c0'
    __payload_type__ = 'a{ss}'

    info = Column(JSONB, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'info': get_asv_dict(payload)}


class DiscoveryFeedOpened(SingularEvent):
    __tablename__ = 'discovery_feed_opened'
    __event_uuid__ = 'd54cbd8c-c977-4dac-ae72-535ad5633877'
    __payload_type__ = 'a{ss}'

    info = Column(JSONB, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'info': get_asv_dict(payload)}


class DiskSpaceExtra(SingularEvent):
    __tablename__ = 'disk_space_extra'
    __event_uuid__ = 'da505554-4248-4a38-bb32-84ab58e45a6d'
    __payload_type__ = '(uuu)'

    total = Column(BigInteger, nullable=False)
    used = Column(BigInteger, nullable=False)
    free = Column(BigInteger, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'total': payload.get_child_value(0).get_uint32(),
            'used': payload.get_child_value(1).get_uint32(),
            'free': payload.get_child_value(2).get_uint32(),
        }


class DiskSpaceSysroot(SingularEvent):
    __tablename__ = 'disk_space_sysroot'
    __event_uuid__ = '5f58024f-3b99-47d3-a17f-1ec876acd97e'
    __payload_type__ = '(uuu)'

    total = Column(BigInteger, nullable=False)
    used = Column(BigInteger, nullable=False)
    free = Column(BigInteger, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'total': payload.get_child_value(0).get_uint32(),
            'used': payload.get_child_value(1).get_uint32(),
            'free': payload.get_child_value(2).get_uint32(),
        }


class DualBootBooted(SingularEvent):
    __tablename__ = 'dual_boot_booted'
    __event_uuid__ = '16cfc671-5525-4a99-9eb9-4f6c074803a9'
    __payload_type__ = None


class EndlessApplicationUnmaximized(SingularEvent):
    __tablename__ = 'endless_application_unmaximized'
    __event_uuid__ = '2b5c044d-d819-4e2c-a3a6-c485c1ac371e'
    __payload_type__ = 's'

    app_id = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'app_id': payload.get_string()}


class HackClubhouseAchievement(SingularEvent):
    __tablename__ = 'hack_clubhouse_achievement'
    __event_uuid__ = '62ce2e93-bfdc-4cae-af4c-54068abfaf02'
    __payload_type__ = '(ss)'

    achievement_id = Column(Unicode, nullable=False)
    achievement_name = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'achievement_id': payload.get_child_value(0).get_string(),
            'achievement_name': payload.get_child_value(1).get_string(),
        }


class HackClubhouseAchievementPoints(SingularEvent):
    __tablename__ = 'hack_clubhouse_achievement_points'
    __event_uuid__ = '86521913-bfa3-4d13-b511-a03d4e339d2f'
    __payload_type__ = '(sii)'

    skillset = Column(Unicode, nullable=False)
    points = Column(Integer, nullable=False)
    new_points = Column(Integer, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'skillset': payload.get_child_value(0).get_string(),
            'points': payload.get_child_value(1).get_int32(),
            'new_points': payload.get_child_value(2).get_int32(),
        }


class HackClubhouseChangePage(SingularEvent):
    __tablename__ = 'hack_clubhouse_change_page'
    __event_uuid__ = '2c765b36-a4c9-40ee-b313-dc73c4fa1f0d'
    __payload_type__ = 's'

    page = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'page': payload.get_string()}


class HackClubhouseEnterPathway(SingularEvent):
    __tablename__ = 'hack_clubhouse_enter_pathway'
    __event_uuid__ = '600c1cae-b391-4cb4-9930-ea284792fdfb'
    __payload_type__ = 's'

    pathway = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'pathway': payload.get_string()}


class HackClubhouseMode(SingularEvent):
    __tablename__ = 'hack_clubhouse_mode'
    __event_uuid__ = '7587784b-c3ed-4d74-b0fa-1023033698c0'
    __payload_type__ = 'b'

    active = Column(Boolean, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'active': payload.get_boolean()}


class HackClubhouseProgress(SingularEvent):
    __tablename__ = 'hack_clubhouse_progress'
    __event_uuid__ = '3a037364-9164-4b42-8c07-73bcc00902de'
    __payload_type__ = 'a{sv}'

    complete = Column(Boolean, nullable=False)
    quest = Column(Unicode, nullable=False)
    pathways = Column(ARRAY(Unicode, dimensions=1), nullable=False)
    progress = Column(Numeric, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        result: Dict[str, Any] = {}

        for item in get_child_values(payload):
            name = item.get_child_value(0).get_string()
            value = item.get_child_value(1).get_variant()

            if name == 'complete':
                result['complete'] = value.get_boolean()

            elif name == 'quest':
                result['quest'] = value.get_string()

            elif name == 'pathways':
                result['pathways'] = get_strings(value)

            elif name == 'progress':
                result['progress'] = value.get_double()

        keys = sorted(result.keys())

        if keys != ['complete', 'pathways', 'progress', 'quest']:
            raise ValueError(f'Metric event 3a037364-9164-4b42-8c07-73bcc00902de needs an '
                             '"a{sv}" payload with certain keys, but some were missing: got '
                             f'{keys}')

        return result


class ImageVersion(SingularEvent):
    __tablename__ = 'image_version'
    __event_uuid__ = '6b1c1cfc-bc36-438c-0647-dacd5878f2b3'
    __payload_type__ = 's'

    image_id = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'image_id': payload.get_string()}


@listens_for(DbSession, 'before_commit')
def receive_before_commit(dbsession: DbSession) -> None:
    for instance in dbsession.new:
        if not isinstance(instance, ImageVersion):
            continue

        insert_machine(dbsession, instance.request.machine_id, image_id=instance.image_id)


class LaunchedEquivalentExistingFlatpak(SingularEvent):
    __tablename__ = 'launched_equivalent_existing_flatpak'
    __event_uuid__ = '00d7bc1e-ec93-4c53-ae78-a6b40450be4a'
    __payload_type__ = '(sas)'

    replacement_app_id = Column(Unicode, nullable=False)
    argv = Column(ARRAY(Unicode, dimensions=1), nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'replacement_app_id': payload.get_child_value(0).get_string(),
            'argv': get_strings(payload.get_child_value(1)),
        }


class LaunchedEquivalentInstallerForFlatpak(SingularEvent):
    __tablename__ = 'launched_equivalent_installer_for_flatpak'
    __event_uuid__ = '7de69d43-5f6b-4bef-b5f3-a21295b79185'
    __payload_type__ = '(sas)'

    replacement_app_id = Column(Unicode, nullable=False)
    argv = Column(ARRAY(Unicode, dimensions=1), nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'replacement_app_id': payload.get_child_value(0).get_string(),
            'argv': get_strings(payload.get_child_value(1)),
        }


class LaunchedExistingFlatpak(SingularEvent):
    __tablename__ = 'launched_existing_flatpak'
    __event_uuid__ = '192f39dd-79b3-4497-99fa-9d8aea28760c'
    __payload_type__ = '(sas)'

    replacement_app_id = Column(Unicode, nullable=False)
    argv = Column(ARRAY(Unicode, dimensions=1), nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'replacement_app_id': payload.get_child_value(0).get_string(),
            'argv': get_strings(payload.get_child_value(1)),
        }


class LaunchedInstallerForFlatpak(SingularEvent):
    __tablename__ = 'launched_installer_for_flatpak'
    __event_uuid__ = 'e98bf6d9-8511-44f9-a1bd-a1d0518934b9'
    __payload_type__ = '(sas)'

    replacement_app_id = Column(Unicode, nullable=False)
    argv = Column(ARRAY(Unicode, dimensions=1), nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'replacement_app_id': payload.get_child_value(0).get_string(),
            'argv': get_strings(payload.get_child_value(1)),
        }


class LinuxPackageOpened(SingularEvent):
    __tablename__ = 'linux_package_opened'
    __event_uuid__ = '0bba3340-52e3-41a2-854f-e6ed36621379'
    __payload_type__ = 'as'

    argv = Column(ARRAY(Unicode, dimensions=1), nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'argv': get_strings(payload),
        }


class LiveUsbBooted(SingularEvent):
    __tablename__ = 'live_usb_booted'
    __event_uuid__ = '56be0b38-e47b-4578-9599-00ff9bda54bb'
    __payload_type__ = None


class Location(SingularEvent):
    __tablename__ = 'location'
    __event_uuid__ = 'abe7af92-6704-4d34-93cf-8f1b46eb09b8'
    __payload_type__ = '(ddbdd)'

    latitude = Column(DOUBLE_PRECISION, nullable=False)
    longitude = Column(DOUBLE_PRECISION, nullable=False)
    altitude = Column(DOUBLE_PRECISION)  # This is optional
    accuracy = Column(DOUBLE_PRECISION, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        has_altitude = payload.get_child_value(2).get_boolean()

        return {
            'latitude': payload.get_child_value(0).get_double(),
            'longitude': payload.get_child_value(1).get_double(),
            'altitude': payload.get_child_value(3).get_double() if has_altitude else None,
            'accuracy': payload.get_child_value(4).get_double(),
        }


class LocationLabel(SingularEvent):
    __tablename__ = 'location_event'
    __event_uuid__ = 'eb0302d8-62e7-274b-365f-cd4e59103983'
    __payload_type__ = 'a{ss}'

    info = Column(JSONB, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'info': get_asv_dict(payload)}


class MissingCodec(SingularEvent):
    __tablename__ = 'missing_codec'
    __event_uuid__ = '74ceec37-1f66-486e-99b0-d39b23daa113'
    __payload_type__ = '(ssssa{sv})'

    gstreamer_version = Column(Unicode, nullable=False)
    app_name = Column(Unicode, nullable=False)
    type = Column(Unicode, nullable=False)
    name = Column(Unicode, nullable=False)
    extra_info = Column(JSONB, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'gstreamer_version': payload.get_child_value(0).get_string(),
            'app_name': payload.get_child_value(1).get_string(),
            'type': payload.get_child_value(2).get_string(),
            'name': payload.get_child_value(3).get_string(),
            'extra_info': get_asv_dict(payload.get_child_value(4)),
        }


class MonitorConnected(SingularEvent):
    __tablename__ = 'monitor_connected'
    __event_uuid__ = 'fa82f422-a685-46e4-91a7-7b7bfb5b289f'

    # The 4th field is the serial number of the monitor, we ignore it as it could identify people
    __payload_type__ = '(ssssiiay)'

    display_name = Column(Unicode, nullable=False)
    display_vendor = Column(Unicode, nullable=False)
    display_product = Column(Unicode, nullable=False)
    display_width = Column(Integer, nullable=False)
    display_height = Column(Integer, nullable=False)
    edid = Column(LargeBinary, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'display_name': payload.get_child_value(0).get_string(),
            'display_vendor': payload.get_child_value(1).get_string(),
            'display_product': payload.get_child_value(2).get_string(),
            'display_width': payload.get_child_value(4).get_int32(),
            'display_height': payload.get_child_value(5).get_int32(),
            'edid': get_bytes(payload.get_child_value(6)),
        }


class MonitorDisconnected(SingularEvent):
    __tablename__ = 'monitor_disconnected'
    __event_uuid__ = '5e8c3f40-22a2-4d5d-82f3-e3bf927b5b74'

    # The 4th field is the serial number of the monitor, we ignore it as it could identify people
    __payload_type__ = '(ssssiiay)'

    display_name = Column(Unicode, nullable=False)
    display_vendor = Column(Unicode, nullable=False)
    display_product = Column(Unicode, nullable=False)
    display_width = Column(Integer, nullable=False)
    display_height = Column(Integer, nullable=False)
    edid = Column(LargeBinary, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'display_name': payload.get_child_value(0).get_string(),
            'display_vendor': payload.get_child_value(1).get_string(),
            'display_product': payload.get_child_value(2).get_string(),
            'display_width': payload.get_child_value(4).get_int32(),
            'display_height': payload.get_child_value(5).get_int32(),
            'edid': get_bytes(payload.get_child_value(6)),
        }


class NetworkId(SingularEvent):
    __tablename__ = 'network_id'
    __event_uuid__ = '38eb48f8-e131-9b57-77c6-35e0590c82fd'
    __payload_type__ = 'u'

    network_id = Column(BigInteger, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'network_id': payload.get_uint32()}


class OSVersion(SingularEvent):
    __tablename__ = 'os_version'
    __event_uuid__ = '1fa16a31-9225-467e-8502-e31806e9b4eb'

    # The 3rd field is now obsolete and ignored, so we only parse and store the first 2
    __payload_type__ = '(sss)'

    name = Column(Unicode, nullable=False)
    version = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'name': payload.get_child_value(0).get_string(),
            'version': payload.get_child_value(1).get_string(),
        }


class ProgramDumpedCore(SingularEvent):
    __tablename__ = 'program_dumped_core'
    __event_uuid__ = 'ed57b607-4a56-47f1-b1e4-5dc3e74335ec'
    __payload_type__ = 'a{sv}'

    info = Column(JSONB, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'info': get_asv_dict(payload)}


class RAMSize(SingularEvent):
    __tablename__ = 'ram_size'
    __event_uuid__ = 'aee94585-07a2-4483-a090-25abda650b12'
    __payload_type__ = 'u'

    total = Column(BigInteger, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'total': payload.get_uint32()}


class ShellAppAddedToDesktop(SingularEvent):
    __tablename__ = 'shell_app_added_to_desktop'
    __event_uuid__ = '51640a4e-79aa-47ac-b7e2-d3106a06e129'
    __payload_type__ = 's'

    app_id = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'app_id': payload.get_string()}


class ShellAppRemovedFromDesktop(SingularEvent):
    __tablename__ = 'shell_app_removed_from_desktop'
    __event_uuid__ = '683b40a7-cac0-4f9a-994c-4b274693a0a0'
    __payload_type__ = 's'

    app_id = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'app_id': payload.get_string()}


class UpdaterBranchSelected(SingularEvent):
    __tablename__ = 'updater_branch_selected'
    __event_uuid__ = '99f48aac-b5a0-426d-95f4-18af7d081c4e'
    __payload_type__ = '(sssb)'

    hardware_vendor = Column(Unicode, nullable=False)
    hardware_product = Column(Unicode, nullable=False)
    ostree_branch = Column(Unicode, nullable=False)
    on_hold = Column(Boolean, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'hardware_vendor': normalize_vendor(payload.get_child_value(0).get_string()),
            'hardware_product': payload.get_child_value(1).get_string(),
            'ostree_branch': payload.get_child_value(2).get_string(),
            'on_hold': payload.get_child_value(3).get_boolean(),
        }


class Uptime(SingularEvent):
    __tablename__ = 'uptime'
    __event_uuid__ = '9af2cc74-d6dd-423f-ac44-600a6eee2d96'
    __payload_type__ = '(xx)'

    accumulated_uptime = Column(BigInteger, nullable=False)
    number_of_boots = Column(BigInteger, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'accumulated_uptime': payload.get_child_value(0).get_int64(),
            'number_of_boots': payload.get_child_value(1).get_int64(),
        }


class WindowsAppOpened(SingularEvent):
    __tablename__ = 'windows_app_opened'
    __event_uuid__ = 'cf09194a-3090-4782-ab03-87b2f1515aed'
    __payload_type__ = 'as'

    argv = Column(ARRAY(Unicode, dimensions=1), nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'argv': get_strings(payload),
        }


class WindowsLicenseTables(SingularEvent):
    __tablename__ = 'windows_license_tables'
    __event_uuid__ = 'ef74310f-7c7e-ca05-0e56-3e495973070a'
    __payload_type__ = 'u'

    # This comes in as a uint32, but PostgreSQL only has signed types so we need a BIGINT (int64)
    tables = Column(BigInteger, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'tables': payload.get_uint32()}


# -- Aggregate events ---------------------------------------------------------

# TODO: Add aggregate event implementations here


# -- Sequence events ----------------------------------------------------------

class ShellAppIsOpen(SequenceEvent):
    __tablename__ = 'shell_app_is_open'
    __event_uuid__ = 'b5e11a3d-13f8-4219-84fd-c9ba0bf3d1f0'
    __payload_type__ = 's'

    app_id = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'app_id': payload.get_string()}


class UserIsLoggedIn(SequenceEvent):
    __tablename__ = 'user_id_logged_in'
    __event_uuid__ = 'add052be-7b2a-4959-81a5-a7f45062ee98'
    __payload_type__ = 'u'

    logged_in_user_id = Column(BigInteger, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'logged_in_user_id': payload.get_uint32()}
