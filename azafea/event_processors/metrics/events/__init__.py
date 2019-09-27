# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from typing import Any, Dict

from gi.repository import GLib

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.schema import Column
from sqlalchemy.types import ARRAY, BigInteger, Boolean, Integer, LargeBinary, Unicode

from azafea.vendors import normalize_vendor
from ..utils import get_asv_dict, get_bytes, get_strings
from ._base import (  # noqa: F401
    SequenceEvent,
    SingularEvent,
    # Reexport some symbols
    new_aggregate_event,
    new_sequence_event,
    new_singular_event,
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


class ImageVersion(SingularEvent):
    __tablename__ = 'image_version'
    __event_uuid__ = '6b1c1cfc-bc36-438c-0647-dacd5878f2b3'
    __payload_type__ = 's'

    image_id = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'image_id': payload.get_string()}


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
            'display_vendor': normalize_vendor(payload.get_child_value(1).get_string()),
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
            'display_vendor': normalize_vendor(payload.get_child_value(1).get_string()),
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


class NetworkStatusChanged(SingularEvent):
    __tablename__ = 'network_status_changed'
    __event_uuid__ = '5fae6179-e108-4962-83be-c909259c0584'
    __payload_type__ = '(uu)'

    previous_state = Column(BigInteger, nullable=False)
    new_state = Column(BigInteger, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'previous_state': payload.get_child_value(0).get_uint32(),
            'new_state': payload.get_child_value(1).get_uint32(),
        }


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

    payload = Column(JSONB, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'payload': get_asv_dict(payload)}


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
