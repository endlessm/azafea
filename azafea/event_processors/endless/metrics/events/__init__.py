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
from sqlalchemy.engine.default import DefaultExecutionContext
from sqlalchemy.event import listens_for
from sqlalchemy.inspection import inspect
from sqlalchemy.schema import Column, Index
from sqlalchemy.types import (
    ARRAY,
    BigInteger,
    Boolean,
    Float,
    Integer,
    LargeBinary,
    Numeric,
    Unicode,
)

from azafea.model import Base, DbSession
from azafea.vendors import normalize_vendor
from ..machine import (
    upsert_machine_demo,
    upsert_machine_dualboot,
    upsert_machine_image,
    upsert_machine_live,
    upsert_machine_location,
)
from ..utils import clamp_to_int64, get_bytes, get_child_values
from ._base import (  # noqa: F401
    EmptyPayloadError,
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


class ControlCenterAutomaticUpdates(SingularEvent):
    __tablename__ = 'control_center_automatic_updates'
    __event_uuid__ = '510f9741-823e-41a9-af2d-048895f990c0'
    __payload_type__ = '(bbbv)'

    allow_downloads_when_metered = Column(Boolean, nullable=False)
    automatic_updates_enabled = Column(Boolean, nullable=False)
    tariff_enabled = Column(Boolean, nullable=False)
    tariff_variant = Column(JSONB, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'allow_downloads_when_metered': payload.get_child_value(0).get_boolean(),
            'automatic_updates_enabled': payload.get_child_value(1).get_boolean(),
            'tariff_enabled': payload.get_child_value(2).get_boolean(),
            'tariff_variant': payload.get_child_value(3).unpack(),
        }


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
        return {'info': payload.unpack()}


class DiscoveryFeedClosed(SingularEvent):
    __tablename__ = 'discovery_feed_closed'
    __event_uuid__ = 'e7932cbd-7c20-49eb-94e9-4bf075e0c0c0'
    __payload_type__ = 'a{ss}'

    info = Column(JSONB, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'info': payload.unpack()}


class DiscoveryFeedOpened(SingularEvent):
    __tablename__ = 'discovery_feed_opened'
    __event_uuid__ = 'd54cbd8c-c977-4dac-ae72-535ad5633877'
    __payload_type__ = 'a{ss}'

    info = Column(JSONB, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'info': payload.unpack()}


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


class EnteredDemoMode(SingularEvent):
    __tablename__ = 'entered_demo_mode'
    __event_uuid__ = 'c75af67f-cf2f-433d-a060-a670087d93a1'
    __payload_type__ = None


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


class HackClubhouseNewsQuestLink(SingularEvent):
    __tablename__ = 'hack_clubhouse_news_quest_link'
    __event_uuid__ = 'ebffecb9-7b31-4c30-a9a0-f896aaaa5b4f'
    __payload_type__ = '(ss)'

    character = Column(Unicode, nullable=False)
    quest = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'character': payload.get_child_value(0).get_string(),
            'quest': payload.get_child_value(1).get_string(),
        }


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
                result['pathways'] = value.unpack()

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
            'argv': payload.get_child_value(1).unpack(),
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
            'argv': payload.get_child_value(1).unpack(),
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
            'argv': payload.get_child_value(1).unpack(),
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
            'argv': payload.get_child_value(1).unpack(),
        }


class LinuxPackageOpened(SingularEvent):
    __tablename__ = 'linux_package_opened'
    __event_uuid__ = '0bba3340-52e3-41a2-854f-e6ed36621379'
    __payload_type__ = 'as'

    argv = Column(ARRAY(Unicode, dimensions=1), nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'argv': payload.unpack(),
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
    __ignore_empty_payload__ = True

    info = Column(JSONB, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        # Empty values are removed as they are useless, even if they are sent
        # by old versions of eos-metrics-instrumentation
        info = {key: value for (key, value) in payload.unpack().items() if value}
        if not info:
            raise EmptyPayloadError('Location label event received with no data.')
        return {'info': info}


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
            'extra_info': payload.get_child_value(4).unpack(),
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

    # The 1st and 3rd fields are now obsolete and ignored, so we only parse and store the 2nd one
    __payload_type__ = '(sss)'

    version = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'version': payload.get_child_value(1).get_string().strip('"'),
        }


class ParentalControlsBlockedFlatpakInstall(SingularEvent):
    __tablename__ = 'parental_controls_blocked_flatpak_install'
    __event_uuid__ = '9d03daad-f1ed-41a8-bc5a-6b532c075832'
    __payload_type__ = 's'

    app = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'app': payload.get_string(),
        }


class ParentalControlsBlockedFlatpakRun(SingularEvent):
    __tablename__ = 'parental_controls_blocked_flatpak_run'
    __event_uuid__ = 'afca2515-e9ce-43aa-b355-7663c770b4b6'
    __payload_type__ = 's'

    app = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'app': payload.get_string(),
        }


class ParentalControlsChanged(SingularEvent):
    __tablename__ = 'parental_controls_changed'
    __event_uuid__ = '449ec188-cb7b-45d3-a0ed-291d943b9aa6'
    __payload_type__ = 'a{sv}'

    # The a{sv} contains the fields from
    # `com.endlessm.ParentalControls.AppFilter`. The a{sv} describes the new
    # parental controls settings for one user. It may also contain the following
    # additional optional fields:
    #  - IsAdministrator (`b`): whether the user is an administrator
    #  - IsInitialSetup (`b`): whether this event is happening during gnome-initial-setup
    app_filter_is_whitelist = Column(Boolean, nullable=False)
    app_filter = Column(ARRAY(Unicode, dimensions=1), nullable=False)
    oars_filter = Column(JSONB, nullable=False)
    allow_user_installation = Column(Boolean, nullable=False)
    allow_system_installation = Column(Boolean, nullable=False)
    is_administrator = Column(Boolean, nullable=False)
    is_initial_setup = Column(Boolean, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        # Default values, as some a{sv} fields are optional:
        result: Dict[str, Any] = {
            'is_administrator': False,
            'is_initial_setup': False,
        }

        for item in get_child_values(payload):
            name = item.get_child_value(0).get_string()
            value = item.get_child_value(1).get_variant()

            if name == 'AppFilter':
                result['app_filter_is_whitelist'] = \
                    value.get_child_value(0).get_boolean()
                result['app_filter'] = value.get_child_value(1).unpack()

            elif name == 'OarsFilter':
                if value.get_child_value(0).get_string() not in ['oars-1.0', 'oars-1.1']:
                    raise ValueError('Metric event '
                                     f'{ParentalControlsChanged.__event_uuid__} '
                                     'needs an "OarsFilter" key in oars-1.0 '
                                     'or oars-1.1 format, but actually got '
                                     f'{payload}')
                result['oars_filter'] = value.get_child_value(1).unpack()

            elif name == 'AllowUserInstallation':
                result['allow_user_installation'] = value.get_boolean()

            elif name == 'AllowSystemInstallation':
                result['allow_system_installation'] = value.get_boolean()

            elif name == 'IsAdministrator':
                result['is_administrator'] = value.get_boolean()

            elif name == 'IsInitialSetup':
                result['is_initial_setup'] = value.get_boolean()

        if result.keys() < {'app_filter_is_whitelist', 'app_filter',
                            'oars_filter', 'allow_user_installation',
                            'allow_system_installation', 'is_administrator',
                            'is_initial_setup'}:
            raise ValueError('Metric event '
                             f'{ParentalControlsChanged.__event_uuid__} '
                             'needs an "a{sv}" payload with certain keys, but '
                             f'some were missing: got {payload}')

        return result


class ParentalControlsEnabled(SingularEvent):
    __tablename__ = 'parental_controls_enabled'
    __event_uuid__ = 'c227a817-808c-4fcb-b797-21002d17b69a'
    __payload_type__ = 'b'

    enabled = Column(Boolean, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'enabled': payload.get_boolean(),
        }


class ProgramDumpedCore(SingularEvent):
    __tablename__ = 'program_dumped_core'
    __event_uuid__ = 'ed57b607-4a56-47f1-b1e4-5dc3e74335ec'
    __payload_type__ = 'a{sv}'

    info = Column(JSONB, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'info': payload.unpack()}


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


class UnderscanEnabled(SingularEvent):
    __tablename__ = 'underscan_enabled'
    __event_uuid__ = '304662c0-fdce-46b8-aa39-d1beb097efcd'
    __payload_type__ = None


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


class UpdaterFailure(SingularEvent):
    __tablename__ = 'updater_failure'
    __event_uuid__ = '927d0f61-4890-4912-a513-b2cb0205908f'
    __payload_type__ = '(ss)'

    component = Column(Unicode, nullable=False)
    error_message = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'component': payload.get_child_value(0).get_string(),
            'error_message': payload.get_child_value(1).get_string(),
        }


class Uptime(SingularEvent):
    __tablename__ = 'uptime'
    __event_uuid__ = '9af2cc74-d6dd-423f-ac44-600a6eee2d96'
    __payload_type__ = '(xx)'
    __ignore_empty_payload__ = True

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
            'argv': payload.unpack(),
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


class CacheHasInvalidElements(SingularEvent):
    """Some invalid cache elements were found.

    We've observed that in some situations the metrics recorder daemon's cached
    data contains only a few valid items and then corrupt data, and that some
    other times the whole thing becomes corrupt and completely unusable,
    bringing down the whole metrics recorder daemon and effectively killing
    metrics reporting forever for that machine.

    As it's still unclear why that happens, we now detect those situations and
    correct them when they happen, so that the metrics system can still be used
    afterwards.

    :UUID name: ``CACHE_HAS_INVALID_ELEMENTS_EVENT_ID`` in eos-event-recorder-daemon

    .. versionadded:: 3.0.9

    """
    __tablename__ = 'cache_has_invalid_elements'
    __event_uuid__ = 'cbfbcbdb-6af2-f1db-9e11-6cc25846e296'
    __payload_type__ = '(tt)'

    # These come in as uint64, but the values won’t reach the limit of a BIGINT (int64, 2**63):
    # - 2**63 elements ≈ 10 billions billions elements
    # - 2**63 bytes ≈ 8,000,000 TB
    #: number of valid elements found in the cache
    number_of_valid_elements = Column(BigInteger, nullable=False)
    #: total number of bytes read from the cache
    number_of_bytes_read = Column(BigInteger, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'number_of_valid_elements': clamp_to_int64(payload.get_child_value(0).get_uint64()),
            'number_of_bytes_read': clamp_to_int64(payload.get_child_value(1).get_uint64()),
        }


class StartupFinished(SingularEvent):
    """Computer startup finishes.

    We send this event when startup finishes with a breakdown of how long was
    spent in each of several different phases of startup.

    The value comes directly from `systemd’s StartupFinished signal
    <https://www.freedesktop.org/wiki/Software/systemd/dbus/\
    #Manager-StartupFinished>`_.

    :UUID name: ``STARTUP_FINISHED`` in eos-metrics-instrumentation

    .. versionadded:: 2.1.2

    """
    __tablename__ = 'startup_finished'
    __event_uuid__ = 'bf7e8aed-2932-455c-a28e-d407cfd5aaba'
    __payload_type__ = '(tttttt)'

    # These come in as uint64, but the values won’t reach the limit of a BIGINT (int64, 2**63):
    # 2**63 microseconds ≈ 300,000 years
    #: time spent in the firmware (if known) in µsec
    firmware = Column(BigInteger, nullable=False)
    #: time spent in the boot loader (if known) in µsec
    loader = Column(BigInteger, nullable=False)
    #: time spent in the kernel initialization phase in µsec
    kernel = Column(BigInteger, nullable=False)
    #: time spent in the initrd (if known) in µsec
    initrd = Column(BigInteger, nullable=False)
    #: time spent in userspace in µsec
    userspace = Column(BigInteger, nullable=False)
    #: total time spent to boot in µsec
    total = Column(BigInteger, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'firmware': clamp_to_int64(payload.get_child_value(0).get_uint64()),
            'loader': clamp_to_int64(payload.get_child_value(1).get_uint64()),
            'kernel': clamp_to_int64(payload.get_child_value(2).get_uint64()),
            'initrd': clamp_to_int64(payload.get_child_value(3).get_uint64()),
            'userspace': clamp_to_int64(payload.get_child_value(4).get_uint64()),
            'total': clamp_to_int64(payload.get_child_value(5).get_uint64()),
        }


# -- Aggregate events ---------------------------------------------------------

# TODO: Add aggregate event implementations here


# -- Sequence events ----------------------------------------------------------

def default_time_duration(context: DefaultExecutionContext) -> float:
    # FIXME: sqlalchemy-stubs doesn’t include get_current_parameters
    parameters = context.get_current_parameters()  # type: ignore
    return (parameters['stopped_at'] - parameters['started_at']).total_seconds()


class ShellAppIsOpen(SequenceEvent):
    __tablename__ = 'shell_app_is_open'
    __event_uuid__ = 'b5e11a3d-13f8-4219-84fd-c9ba0bf3d1f0'
    __payload_type__ = 's'

    app_id = Column(Unicode, nullable=False)
    duration = Column(Float, default=default_time_duration, nullable=False)

    __table_args__ = (
        Index('ix_shell_app_is_open_app_id_started_at', 'app_id', 'started_at',
              postgresql_ops={'app_id': 'varchar_pattern_ops'}),
    )

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'app_id': payload.get_string()}


class UserIsLoggedIn(SequenceEvent):
    __tablename__ = 'user_id_logged_in'
    __event_uuid__ = 'add052be-7b2a-4959-81a5-a7f45062ee98'
    __payload_type__ = 'u'
    __ignore_empty_payload__ = True

    logged_in_user_id = Column(BigInteger, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'logged_in_user_id': payload.get_uint32()}


# -- Model listeners ----------------------------------------------------------

@listens_for(DbSession, 'after_attach')
def receive_after_attach(dbsession: DbSession, instance: Base) -> None:
    if not isinstance(instance, (DualBootBooted, ImageVersion, LiveUsbBooted)):
        return

    # So we have just added an event to the session, but we only want to keep it if there
    # wasn't already a pending one for the same metrics request

    instance_type = type(instance)

    pending_events_of_same_type = (
        x for x in dbsession.new
        if isinstance(x, instance_type) and inspect(x).pending
    )
    pending_events_of_same_type_in_same_request = [
        # Requests don't have an id yet, because they have just been added to the db session which
        # hasn't been committed yet; their sha512 is a good replacement identifier given that we
        # have a unicity constraint on them
        x for x in pending_events_of_same_type if x.request.sha512 == instance.request.sha512
    ]

    if len(pending_events_of_same_type_in_same_request) > 1:
        dbsession.expunge(instance)


@listens_for(DbSession, 'before_commit')
def receive_before_commit(dbsession: DbSession) -> None:
    for instance in dbsession.new:
        if isinstance(instance, ImageVersion):
            # Resolve instance.request even if dbsession is not flushed yet
            dbsession.enable_relationship_loading(instance)
            upsert_machine_image(dbsession, instance.request.machine_id, image_id=instance.image_id)

        elif isinstance(instance, DualBootBooted):
            dbsession.enable_relationship_loading(instance)
            upsert_machine_dualboot(dbsession, instance.request.machine_id)

        elif isinstance(instance, EnteredDemoMode):
            dbsession.enable_relationship_loading(instance)
            upsert_machine_demo(dbsession, instance.request.machine_id)

        elif isinstance(instance, LiveUsbBooted):
            dbsession.enable_relationship_loading(instance)
            upsert_machine_live(dbsession, instance.request.machine_id)

        elif isinstance(instance, LocationLabel):
            dbsession.enable_relationship_loading(instance)
            upsert_machine_location(dbsession, instance.request.machine_id, info=instance.info)
