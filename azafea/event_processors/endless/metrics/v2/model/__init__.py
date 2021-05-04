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
from ..utils import clamp_to_int64, get_bytes, get_child_values
from ._base import (  # noqa: F401
    AGGREGATE_EVENT_MODELS,
    SEQUENCE_EVENT_MODELS,
    SINGULAR_EVENT_MODELS,
    AggregateEvent,
    EmptyPayloadError,
    InvalidAggregateEvent,
    InvalidSequence,
    InvalidSingularEvent,
    SequenceEvent,
    SingularEvent,
    UnknownAggregateEvent,
    UnknownEvent,
    UnknownSequence,
    UnknownSingularEvent,
    WrongPayloadError,
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
from ._machine import (  # noqa: F401
    Machine,
    upsert_machine_demo,
    upsert_machine_dualboot,
    upsert_machine_image,
    upsert_machine_live,
    upsert_machine_location,
)
from ._request import MachineIdsByDay, Request, RequestBuilder  # noqa: F401


# -- Singular events ----------------------------------------------------------

class CacheIsCorrupt(SingularEvent):
    """Cache has been found to be corrupt and was reset.

    We've observed that in some situations the metrics recorder daemon's cached
    data contains only a few valid items and then corrupt data, and that some
    other times the whole thing becomes corrupt and completely unusable,
    bringing down the whole metrics recorder daemon and effectively killing
    metrics reporting forever for that machine.

    As it's still unclear why that happens, we now detect those situations and
    correct them when they happen, so that the metrics system can still be used
    afterwards.

    :UUID name: ``CACHE_IS_CORRUPT_EVENT_ID`` in eos-event-recorder-daemon

    .. versionadded:: 3.0.9

    """
    __tablename__ = 'cache_is_corrupt'
    __event_uuid__ = 'd84b9a19-9353-73eb-70bf-f91a584abcbd'
    __payload_type__ = None


class CacheMetadataIsCorrupt(SingularEvent):
    """Cache metadata is corrupt and was reset, any cached metrics were discarded.

    We've observed that in some situations the metrics recorder daemon's cached
    data contains only a few valid items and then corrupt data, and that some
    other times the whole thing becomes corrupt and completely unusable,
    bringing down the whole metrics recorder daemon and effectively killing
    metrics reporting forever for that machine.

    As it's still unclear why that happens, we now detect those situations and
    correct them when they happen, so that the metrics system can still be used
    afterwards.

    See `T19953 <https://phabricator.endlessm.com/T19953>`_.

    :UUID name: ``CACHE_METADATA_IS_CORRUPT_EVENT_ID`` in eos-event-recorder-daemon

    .. versionadded:: 3.3.5

    """
    __tablename__ = 'cache_metadata_is_corrupt'
    __event_uuid__ = 'f0e8a206-3bc2-405e-90d0-ef6fe6dd7edc'
    __payload_type__ = None


class ControlCenterAutomaticUpdates(SingularEvent):
    """Automatic updates settings have changed.

    :UUID name: ``CC_METRIC_AUTOMATIC_UPDATES`` in gnome-control-center

    .. versionadded:: 3.9.1

    """
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
    """A panel is open in the control center.

    :UUID name: ``PANEL_OPENED_EVENT_ID`` in gnome-control-center

    .. versionadded:: 3.2.5

    """
    __tablename__ = 'control_center_panel_opened'
    __event_uuid__ = '3c5d59d2-6c3f-474b-95f4-ac6fcc192655'
    __payload_type__ = 's'

    #: panel name (e.g. ``privacy``)
    name = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'name': payload.get_string()}


class CPUInfo(SingularEvent):
    """CPU info, sent on startup.

    See `T18445 <https://phabricator.endlessm.com/T18445>`_.

    :UUID name: ``CPU_MODELS_EVENT``

    .. versionadded:: 3.4.3

    """
    __tablename__ = 'cpu_info'
    __event_uuid__ = '4a75488a-0d9a-4c38-8556-148f500edaf0'
    __payload_type__ = 'a(sqd)'

    #: array of CPU model (e.g. Intel(R) Core(TM) i7-5500U CPU @ 2.40GHz),
    #: number of cores (e.g. 4) and maximum CPU speed in MHz or current CPU speed
    #: if maximum can’t be determined (e.g. 3000.0)
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
    """Something is clicked on the Discovery Feed, including content which is not "clickable".

    The payload tells us about what users are clicking on generally and whether
    they are clicking on things that we don't expect to be clicked. The
    intention is to allow the operator to determine what content should be made
    clickable and what kinds of content are being opened.

    The ``content_type`` field that can be included in the payload is currently
    one of:

    - ``knowledge_content``: text-based article in a knowledge-app
    - ``knowledge_video``: video based article in a knowledge-app
    - ``knowledge_artwork``: "artwork" card (larger images in a "Gallery" style format)
    - ``undefined``: user clicked on a non-clickable area

    :UUID name: ``EVENT_DISCOVERY_FEED_CLICK`` in eos-discovery-feed

    .. versionadded:: 3.2.0

    """
    __tablename__ = 'discovery_feed_clicked'
    __event_uuid__ = 'f2f31a64-2193-42b5-ae39-ca0b4d1f0691'
    __payload_type__ = 'a{ss}'

    #: dictionary of string keys such as ``app_id``, and optionally ``content_type``
    info = Column(JSONB, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'info': payload.unpack()}


class DiscoveryFeedClosed(SingularEvent):
    """The Discovery Feed is closed.

    The payload tells us about how the user is leaving the Discovery Feed and
    how long they spent in it. The intention is to allow the operator to
    determine how users prefer to close the feed (e.g., by clicking outside,
    clicking the close button) and how long users spent in the feed.

    The ``closed_by`` field that is included in the payload is currently any
    one of:

    - ``buttonclose``: user pressed the "X" button in the top right hand corner
    - ``escclose``: user pressed "Escape"
    - ``lost_focus``: user pressed outside the Feed or another window took focus

    :UUID name: ``EVENT_DISCOVERY_FEED_CLOSE`` in eos-discovery-feed

    .. versionadded:: 3.2.0

    """
    __tablename__ = 'discovery_feed_closed'
    __event_uuid__ = 'e7932cbd-7c20-49eb-94e9-4bf075e0c0c0'
    __payload_type__ = 'a{ss}'

    #: dictionary of string keys such as ``closed_by``, ``time`` (time during
    #: which it was opened)
    info = Column(JSONB, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'info': payload.unpack()}


class DiscoveryFeedOpened(SingularEvent):
    """The Discovery Feed is open.

    The payload tells us about the language the user is using when interacting
    with the discovery feed and how they opened it. The intention is to allow
    the operator to determine which languages the discovery feed is most
    popular in and how users generally open the feed.

    :UUID name: ``EVENT_DISCOVERY_FEED_OPEN`` in eos-discovery-feed

    .. versionadded:: 3.2.0

    """
    __tablename__ = 'discovery_feed_opened'
    __event_uuid__ = 'd54cbd8c-c977-4dac-ae72-535ad5633877'
    __payload_type__ = 'a{ss}'

    #: dictionary of string keys such as ``opened_by``, ``language``
    info = Column(JSONB, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'info': payload.unpack()}


class DiskSpaceExtra(SingularEvent):
    """Total, used and free disk space for ``/var/endless-extra``.

    Sent on startup, and every 24 hours.

    See `T18445 <https://phabricator.endlessm.com/T18445>`_.

    :UUID name: ``EXTRA_DISK_SPACE_EVENT`` in eos-metrics-instrumentation

    .. versionadded:: 3.4.3

    """
    __tablename__ = 'disk_space_extra'
    __event_uuid__ = 'da505554-4248-4a38-bb32-84ab58e45a6d'
    __payload_type__ = '(uuu)'

    #: total disk space in gibibytes (2^30)
    total = Column(BigInteger, nullable=False)
    #: used disk space in gibibytes (2^30)
    used = Column(BigInteger, nullable=False)
    #: free disk space in gibibytes (2^30)
    free = Column(BigInteger, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'total': payload.get_child_value(0).get_uint32(),
            'used': payload.get_child_value(1).get_uint32(),
            'free': payload.get_child_value(2).get_uint32(),
        }


class DiskSpaceSysroot(SingularEvent):
    """Total, used and free disk space for ``/``.

    Sent on startup, and every 24 hours.

    See `T18445 <https://phabricator.endlessm.com/T18445>`_.

    :UUID name: ``SYSROOT_DISK_SPACE_EVENT`` in eos-metrics-instrumentation

    .. versionadded:: 3.4.3

    """
    __tablename__ = 'disk_space_sysroot'
    __event_uuid__ = '5f58024f-3b99-47d3-a17f-1ec876acd97e'
    __payload_type__ = '(uuu)'

    #: total disk space in gibibytes (2^30)
    total = Column(BigInteger, nullable=False)
    #: used disk space in gibibytes (2^30)
    used = Column(BigInteger, nullable=False)
    #: free disk space in gibibytes (2^30)
    free = Column(BigInteger, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'total': payload.get_child_value(0).get_uint32(),
            'used': payload.get_child_value(1).get_uint32(),
            'free': payload.get_child_value(2).get_uint32(),
        }


class DualBootBooted(SingularEvent):
    """A dual-boot system boots.

    This allows us to distinguish dual-boot installations from standalone
    installations, whose users may have different patterns of behaviour.

    :UUID name: ``DUAL_BOOT_EVENT`` in eos-metrics-instrumentation

    .. versionadded:: 3.0.6

    """
    __tablename__ = 'dual_boot_booted'
    __event_uuid__ = '16cfc671-5525-4a99-9eb9-4f6c074803a9'
    __payload_type__ = None


class EndlessApplicationUnmaximized(SingularEvent):
    """An in-house application is unmaximized for the first time in each run.

    We record a metric with the application ID.

    :UUID name: ``UNMAXIMIZE_EVENT`` in eos-sdk

    .. versionadded:: 3.0.0

    """
    __tablename__ = 'endless_application_unmaximized'
    __event_uuid__ = '2b5c044d-d819-4e2c-a3a6-c485c1ac371e'
    __payload_type__ = 's'

    #: application ID
    app_id = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'app_id': payload.get_string()}


class EnteredDemoMode(SingularEvent):
    """The systems enters demo mode.

    Note that the machine ID will be reset just before the system enters demo
    mode, so any metrics collected for this machine ID after this event has
    been fired are metrics for a system that is in demo mode.

    Demo mode was removed in EOS 3.9, so this metric will not be seen for
    systems on 3.9.0 or later.

    See `T18983 <https://phabricator.endlessm.com/T18983>`_.

    :UUID name: ``DEMO_MODE_ENTERED_METRIC`` in gnome-initial-setup

    .. versionadded:: 3.2.5

    """
    __tablename__ = 'entered_demo_mode'
    __event_uuid__ = 'c75af67f-cf2f-433d-a060-a670087d93a1'
    __payload_type__ = None


class HackClubhouseAchievement(SingularEvent):
    """Achievement reached in the Hack Clubhouse.

    See `T28004 <https://phabricator.endlessm.com/T28004>`_.

    :UUID name: ``ACHIEVEMENT_EVENT``

    .. versionadded:: 3.7.4

    """
    __tablename__ = 'hack_clubhouse_achievement'
    __event_uuid__ = '62ce2e93-bfdc-4cae-af4c-54068abfaf02'
    __payload_type__ = '(ss)'

    #: achievement ID
    achievement_id = Column(Unicode, nullable=False)
    #: achievement name
    achievement_name = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'achievement_id': payload.get_child_value(0).get_string(),
            'achievement_name': payload.get_child_value(1).get_string(),
        }


class HackClubhouseAchievementPoints(SingularEvent):
    """Points earned in the Hack Clubhouse.

    See `T28004 <https://phabricator.endlessm.com/T28004>`_.

    :UUID name: ``ACHIEVEMENT_POINTS_EVENT``

    .. versionadded:: 3.7.4

    """
    __tablename__ = 'hack_clubhouse_achievement_points'
    __event_uuid__ = '86521913-bfa3-4d13-b511-a03d4e339d2f'
    __payload_type__ = '(sii)'

    #: skillset
    skillset = Column(Unicode, nullable=False)
    #: points earned
    points = Column(Integer, nullable=False)
    #: new points for this user on this skillset
    new_points = Column(Integer, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'skillset': payload.get_child_value(0).get_string(),
            'points': payload.get_child_value(1).get_int32(),
            'new_points': payload.get_child_value(2).get_int32(),
        }


class HackClubhouseChangePage(SingularEvent):
    """Page changed in the Hack Clubhouse.

    See `T28004 <https://phabricator.endlessm.com/T28004>`_.

    :UUID name: ``CLUBHOUSE_SET_PAGE_EVENT``

    .. versionadded:: 3.7.4

    """
    __tablename__ = 'hack_clubhouse_change_page'
    __event_uuid__ = '2c765b36-a4c9-40ee-b313-dc73c4fa1f0d'
    __payload_type__ = 's'

    #: name of the selected page (``CLUBHOUSE`` or ``NEWS`` or ``CHARACTER``)
    page = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'page': payload.get_string()}


class HackClubhouseEnterPathway(SingularEvent):
    """Pathway entered in the Hack Clubhouse.

    See `T28004 <https://phabricator.endlessm.com/T28004>`_.

    :UUID name: ``CLUBHOUSE_PATHWAY_ENTER_EVENT``

    .. versionadded:: 3.7.4

    """
    __tablename__ = 'hack_clubhouse_enter_pathway'
    __event_uuid__ = '600c1cae-b391-4cb4-9930-ea284792fdfb'
    __payload_type__ = 's'

    #: name of the selected pathway
    pathway = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'pathway': payload.get_string()}


class HackClubhouseMode(SingularEvent):
    """Hack mode changed in the Hack Clubhouse.

    See `T28501 <https://phabricator.endlessm.com/T28501>`_.

    :UUID name: ``HACK_MODE_EVENT``

    .. versionadded:: 3.7.4

    """
    __tablename__ = 'hack_clubhouse_mode'
    __event_uuid__ = '7587784b-c3ed-4d74-b0fa-1023033698c0'
    __payload_type__ = 'b'

    #: 1 if the hack mode button is ON after the click, 0 if it is OFF
    active = Column(Boolean, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'active': payload.get_boolean()}


class HackClubhouseNewsQuestLink(SingularEvent):
    """Quest link clicked in the Hack Clubhouse news.

    See `T29192 <https://phabricator.endlessm.com/T29192>`_.

    :UUID name: ``CLUBHOUSE_NEWS_QUEST_LINK_EVENT``

    .. versionadded:: 3.7.4

    """
    __tablename__ = 'hack_clubhouse_news_quest_link'
    __event_uuid__ = 'ebffecb9-7b31-4c30-a9a0-f896aaaa5b4f'
    __payload_type__ = '(ss)'

    #: character in the news item
    character = Column(Unicode, nullable=False)
    #: quest launched ID
    quest = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'character': payload.get_child_value(0).get_string(),
            'quest': payload.get_child_value(1).get_string(),
        }


class HackClubhouseProgress(SingularEvent):
    """Progress updated in the Hack Clubhouse.

    See `T28004 <https://phabricator.endlessm.com/T28004>`_.

    :UUID name: ``PROGRESS_UPDATE_EVENT``

    .. versionadded:: 3.7.4

    """
    __tablename__ = 'hack_clubhouse_progress'
    __event_uuid__ = '3a037364-9164-4b42-8c07-73bcc00902de'
    __payload_type__ = 'a{sv}'

    #: if the quest has been completed or not (boolean)
    complete = Column(Boolean, nullable=False)
    #: ID of the quest that has just finish (string)
    quest = Column(Unicode, nullable=False)
    #: list of pathways of the finished quest (array of string variants)
    pathways = Column(ARRAY(Unicode, dimensions=1), nullable=False)
    #: percentage of quests completed (double)
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
    """The image ID, sent once at startup if present.

    This is a string which is saved in an attribute on the root filesystem by
    the image builder, and allows us to tell the channel that the OS was
    installed by (e.g. download, OEM pre-install, Endless hardware, USB stick,
    etc) and which version was installed. Allows machines with
    deployment-specific images to be found and grouped for metrics analysis
    purposes.

    :UUID name: ``EOS_IMAGE_VERSION_EVENT`` in eos-metrics-instrumentation

    .. versionadded:: 3.1.2

    """
    __tablename__ = 'image_version'
    __event_uuid__ = '6b1c1cfc-bc36-438c-0647-dacd5878f2b3'
    __payload_type__ = 's'

    #: image ID (e.g. ``eos-eos3.1-amd64-amd64.170115-071322.base``)
    image_id = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'image_id': payload.get_string()}


class LaunchedEquivalentExistingFlatpak(SingularEvent):
    """Double-click on Windows exe or Linux package with a similar installed app.

    We launch the native version of a similar application since it is already
    installed. We record shell command line along with any arguments as well as
    the app ID of the replacement application. The purpose of this metric is to
    determine whether transparently launching a similar application reduces
    bounce rate.

    :UUID name: ``EVENT_LAUNCHED_EQUIVALENT_EXISTING_FLATPAK`` in eos-gates

    .. versionadded:: 3.2.4

    """
    __tablename__ = 'launched_equivalent_existing_flatpak'
    __event_uuid__ = '00d7bc1e-ec93-4c53-ae78-a6b40450be4a'
    __payload_type__ = '(sas)'

    #: replacement application ID
    replacement_app_id = Column(Unicode, nullable=False)
    #: argv of the executable (Windows app or Linux package) the user tried to launch
    argv = Column(ARRAY(Unicode, dimensions=1), nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'replacement_app_id': payload.get_child_value(0).get_string(),
            'argv': payload.get_child_value(1).unpack(),
        }


class LaunchedEquivalentInstallerForFlatpak(SingularEvent):
    """Double-click on Windows exe or Linux package with a similar but not installed app in Store.

    We record shell command line along with any arguments as well as the app ID
    of the replacement application. The purpose of this metric is to determine
    whether guiding the user to the app store to install a similar application
    reduces bounce rate.

    :UUID name: ``EVENT_LAUNCHED_EQUIVALENT_INSTALLER_FOR_FLATPAK`` in eos-gates

    .. versionadded:: 3.2.4

    """
    __tablename__ = 'launched_equivalent_installer_for_flatpak'
    __event_uuid__ = '7de69d43-5f6b-4bef-b5f3-a21295b79185'
    __payload_type__ = '(sas)'

    #: replacement application ID
    replacement_app_id = Column(Unicode, nullable=False)
    #: argv of the executable (Windows app or Linux package) the user tried to launch
    argv = Column(ARRAY(Unicode, dimensions=1), nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'replacement_app_id': payload.get_child_value(0).get_string(),
            'argv': payload.get_child_value(1).unpack(),
        }


class LaunchedExistingFlatpak(SingularEvent):
    """Double-click on Windows exe or Linux package with a native installed app.

    We launch the native version of the application since it is already
    installed. We record shell command line along with any arguments as well as
    the app ID of the replacement application. The purpose of this metric is to
    determine whether transparently launching the same application reduces
    bounce rate.

    :UUID name: ``EVENT_LAUNCHED_EXISTING_FLATPAK`` in eos-gates

    .. versionadded:: 3.2.4

    """
    __tablename__ = 'launched_existing_flatpak'
    __event_uuid__ = '192f39dd-79b3-4497-99fa-9d8aea28760c'
    __payload_type__ = '(sas)'

    #: replacement application ID
    replacement_app_id = Column(Unicode, nullable=False)
    #: argv of the executable (Windows app or Linux package) the user tried to launch
    argv = Column(ARRAY(Unicode, dimensions=1), nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'replacement_app_id': payload.get_child_value(0).get_string(),
            'argv': payload.get_child_value(1).unpack(),
        }


class LaunchedInstallerForFlatpak(SingularEvent):
    """Double-click on Windows exe or Linux package with the same but not installed app in Store.

    We record shell command line along with any arguments as well as the app ID
    of the replacement application. The purpose of this metric is to determine
    whether guiding the user to the app store to install the *same* application
    reduces bounce rate.

    :UUID name: ``EVENT_LAUNCHED_INSTALLER_FOR_FLATPAK`` in eos-gates

    .. versionadded:: 3.2.4

    """
    __tablename__ = 'launched_installer_for_flatpak'
    __event_uuid__ = 'e98bf6d9-8511-44f9-a1bd-a1d0518934b9'
    __payload_type__ = '(sas)'

    #: replacement application ID
    replacement_app_id = Column(Unicode, nullable=False)
    #: argv of the executable (Windows app or Linux package) the user tried to launch
    argv = Column(ARRAY(Unicode, dimensions=1), nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'replacement_app_id': payload.get_child_value(0).get_string(),
            'argv': payload.get_child_value(1).unpack(),
        }


class LinuxPackageOpened(SingularEvent):
    """A user tries to open a ``.rpm`` or ``.deb`` file.

    :UUID name: ``LINUX_PACKAGE_OPENED`` in eos-gates

    .. versionadded:: 2.1.7
    """
    __tablename__ = 'linux_package_opened'
    __event_uuid__ = '0bba3340-52e3-41a2-854f-e6ed36621379'
    __payload_type__ = 'as'

    #: argv of the launched Windows application
    argv = Column(ARRAY(Unicode, dimensions=1), nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'argv': payload.unpack(),
        }


class LiveUsbBooted(SingularEvent):
    """A system boots from a combined live + installer USB.

    We expect the metrics reported by live USBs to be a bit weird since they
    are 100% stateless; this metric is intended to help distinguish such
    systems. This event is mutually-exclusive with the dual-boot event above;
    if neither is recorded, the system is a standalone installation.

    :UUID name: ``LIVE_BOOT_EVENT`` in eos-metrics-instrumentation

    .. versionadded:: 3.0.6

    """
    __tablename__ = 'live_usb_booted'
    __event_uuid__ = '56be0b38-e47b-4578-9599-00ff9bda54bb'
    __payload_type__ = None


class Location(SingularEvent):
    """The user’s location at city-level granularity.

    An event is sent once per boot and subsequently every time it changes by a
    distance of 15 km or more during the same boot. We include latitude,
    longitude, altitude if known, and accuracy of the location estimate.

    .. note::

        Since around 3.7.0, for privacy reasons this is only recorded on a
        `small set of products <https://github.com/endlessm/\
        eos-metrics-instrumentation/blob/master/src/eins-location.c#L192-L196>`_
        − at the time of writing this is fnde, impact, payg, solutions, and
        spark. See `T27743 <https://phabricator.endlessm.com/T27743>`_ and
        `T27655 <https://phabricator.endlessm.com/T27655>`_ for more details.

    :UUID name: ``USER_LOCATION`` in eos-metrics-instrumentation

    .. versionadded:: 2.1.5

    """
    __tablename__ = 'location'
    __event_uuid__ = 'abe7af92-6704-4d34-93cf-8f1b46eb09b8'
    __payload_type__ = '(ddbdd)'

    #: latitude
    latitude = Column(DOUBLE_PRECISION, nullable=False)
    #: longitude
    longitude = Column(DOUBLE_PRECISION, nullable=False)
    #: altitude, only set if third payload value is "true"
    altitude = Column(DOUBLE_PRECISION)
    #: accuracy
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
    """Location label at startup or when modified.

    The intention behind the payload is to allow an operator to provide an
    optional human-readable label for the location of the system, which can be
    used when preparing reports or visualisations of the metrics data.

    :UUID name: ``LOCATION_LABEL_EVENT`` in eos-metrics-instrumentation

    .. versionadded:: 3.2.0

    """
    __tablename__ = 'location_event'
    __event_uuid__ = 'eb0302d8-62e7-274b-365f-cd4e59103983'
    __payload_type__ = 'a{ss}'
    __ignore_empty_payload__ = True

    #: dictionary of string keys (such as ``facility``, ``city`` and
    #: ``state``) to the values provided in the location.conf file (written by
    #: the ``eos-label-location`` utility)
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
    """A GStreamer-based application tries to install a missing codec.

    :UUID name: ``EOS_CODECS_MANAGER_MISSING_CODEC`` in eos-codecs-manager

    .. versionadded:: 2.6.0

    """
    __tablename__ = 'missing_codec'
    __event_uuid__ = '74ceec37-1f66-486e-99b0-d39b23daa113'
    __payload_type__ = '(ssssa{sv})'

    #: GStreamer version
    gstreamer_version = Column(Unicode, nullable=False)
    #: application name (not ID)
    app_name = Column(Unicode, nullable=False)
    #: codec type (e.g. decoder)
    type = Column(Unicode, nullable=False)
    #: codec name (MIME type)
    name = Column(Unicode, nullable=False)
    #: extra codec information (e.g. ``{"mpegaudioversion": 1, "mpegversion": 1, "layer": 3}``)
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
    """A display is connected (e.g. computer monitor, television) to the machine.

    We include any information about the display (e.g. with, height).

    :UUID name: ``MONITOR_CONNECTED`` in mutter

    UUID was ``566adb36-7701-4067-a971-a398312c2874`` before 2.1.7.

    .. versionadded:: 2.1.4

    """
    __tablename__ = 'monitor_connected'
    __event_uuid__ = 'fa82f422-a685-46e4-91a7-7b7bfb5b289f'

    # The 4th field is the serial number of the monitor, we ignore it as it could identify people
    __payload_type__ = '(ssssiiay)'

    #: display name
    display_name = Column(Unicode, nullable=False)
    #: display vendor
    display_vendor = Column(Unicode, nullable=False)
    #: display product
    display_product = Column(Unicode, nullable=False)
    #: display width (in mm)
    display_width = Column(Integer, nullable=False)
    #: display height (in mm)
    display_height = Column(Integer, nullable=False)
    #: EDID
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
    """A display is disconnected (e.g. computer monitor, television) from the machine.

    We include any information about the display (e.g. with, height).

    :UUID name: ``MONITOR_DISCONNECTED`` in mutter

    UUID was ``ce179909-dacb-4b7e-83a5-690480bf21eb`` before 2.1.7.

    .. versionadded:: 2.1.4

    """
    __tablename__ = 'monitor_disconnected'
    __event_uuid__ = '5e8c3f40-22a2-4d5d-82f3-e3bf927b5b74'

    # The 4th field is the serial number of the monitor, we ignore it as it could identify people
    __payload_type__ = '(ssssiiay)'

    #: display name
    display_name = Column(Unicode, nullable=False)
    #: display vendor
    display_vendor = Column(Unicode, nullable=False)
    #: display product
    display_product = Column(Unicode, nullable=False)
    #: display width (in mm)
    display_width = Column(Integer, nullable=False)
    #: display height (in mm)
    display_height = Column(Integer, nullable=False)
    #: EDID
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
    """A change in the default route happens after the network connectivity has changed.

    The intention behind the payload is to provide a value which is opaque and
    stable which is the same for every system located on the same physical
    network (also visible from the ``eos-network-id`` command).

    See `T16934 <https://phabricator.endlessm.com/T16934>`_.

    :UUID name: ``NETWORK_ID_EVENT`` in eos-metrics-instrumentation

    .. versionadded:: 3.1.2

    """
    __tablename__ = 'network_id'
    __event_uuid__ = '38eb48f8-e131-9b57-77c6-35e0590c82fd'
    __payload_type__ = 'u'

    #: network ID: a hash of the ethernet MAC address of the gateway, favouring
    #: IPv4 if available, or IPv6 if not
    network_id = Column(BigInteger, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'network_id': payload.get_uint32()}


class OSVersion(SingularEvent):
    """The OS version, recorded at every startup to track deployment statistics.

    To get the personality on current versions, use the last component of the
    :class:`ImageVersion` event.

    :UUID name: ``OS_VERSION_EVENT`` in eos-metrics-instrumentation

    The first (OS name) and third (OS personality) payload fields are now
    obsolete and ignored, so we only parse and store the second one (version).

    .. versionadded:: 2.5.0

    """
    __tablename__ = 'os_version'
    __event_uuid__ = '1fa16a31-9225-467e-8502-e31806e9b4eb'

    __payload_type__ = '(sss)'

    #: current OS version (e.g. ``3.3.0``), taken from ``/etc/os-release``
    version = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'version': payload.get_child_value(1).get_string().strip('"'),
        }


class ParentalControlsBlockedFlatpakInstall(SingularEvent):
    """An app prevented from being installed due to parental controls restrictions.

    This can happen if using the flatpak CLI, or if a UI app fails to hide a
    restricted app from its interface.

    See https://phabricator.endlessm.com/T28741#810046.

    :UUID name: ``FLATPAK_PARENTAL_CONTROLS_INSTALL_EVENT`` in flatpak

    .. versionadded:: 3.8.0

    """
    __tablename__ = 'parental_controls_blocked_flatpak_install'
    __event_uuid__ = '9d03daad-f1ed-41a8-bc5a-6b532c075832'
    __payload_type__ = 's'

    #: flatpak reference for the app which as blocked from being installed
    #: (e.g. ``app/org.gnome.Totem/x86_64/stable``)
    app = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'app': payload.get_string(),
        }


class ParentalControlsBlockedFlatpakRun(SingularEvent):
    """An app prevented from being run due to parental controls restrictions.

    This can happen if using the flatpak CLI, or if a UI app fails to hide a
    restricted app from its interface.

    See https://phabricator.endlessm.com/T28741#810046.

    :UUID name: ``FLATPAK_PARENTAL_CONTROLS_INSTALL_EVENT`` in flatpak

    .. versionadded:: 3.8.0

    """
    __tablename__ = 'parental_controls_blocked_flatpak_run'
    __event_uuid__ = 'afca2515-e9ce-43aa-b355-7663c770b4b6'
    __payload_type__ = 's'

    #: flatpak reference for the app which as blocked from being run
    #: (e.g. ``app/org.gnome.Totem/x86_64/stable``)
    app = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'app': payload.get_string(),
        }


class ParentalControlsChanged(SingularEvent):
    """Parental control app is closed.

    Recorded whenever ``malcontent-control`` is closed, presumably after the
    user has edited one or more parental controls.

    The payload contains the current parental controls settings for one user on
    the system, including identification about whether the user is an
    admin. Other user details (such as username or full name) are not
    included. The event is submitted multiple times, once for each (non-system)
    user on the system.

    The same event is also recorded at the end of Initial Setup if (and only
    if) parental controls were enabled for the main user during Initial
    Setup. In that case, the main user account has been set up as a child user,
    with no administrator privileges, and with parental controls enabled. A
    second user has been created as the administrator. The event contains the
    values of the initial parental controls settings, but no identifying
    information about the user (such as their username or full name). The
    intention is to allow comparisons of which parental controls are enabled
    initially by users, and which are enabled long term.

    See `T28741 <https://phabricator.endlessm.com/T28741#810046>`_ and `#101
    <https://github.com/endlessm/azafea/pull/101#discussion_r402610338>`_.

    The fields in the payload have the same semantics as the properties in the
    `AppFilter <https://gitlab.freedesktop.org/pwithnall/malcontent/-/blob/master/\
    accounts-service/com.endlessm.ParentalControls.AppFilter.xml>` interface.

    :UUID name: ``MCT_PARENTAL_CONTROLS_EVENT`` in malcontent and gnome-initial-setup

    .. versionadded:: 3.8.0

    """
    __tablename__ = 'parental_controls_changed'
    __event_uuid__ = '449ec188-cb7b-45d3-a0ed-291d943b9aa6'
    __payload_type__ = 'a{sv}'

    #: boolean indicating whether the following app filter is a whitelist
    #: (true) or blacklist (false)
    app_filter_is_whitelist = Column(Boolean, nullable=False)
    #: list of strings containing filtered apps (either flatpak refs,
    #: absolute paths, or content types)
    app_filter = Column(ARRAY(Unicode, dimensions=1), nullable=False)
    #: string giving the filter schema (oars-1.0 or oars-1.1 at the moment),
    #: followed by a dictionary mapping OARS category strings to filter levels
    #: (none, mild, moderate, intense)
    oars_filter = Column(JSONB, nullable=False)
    #: boolean indicating whether installation of software to the user flatpak
    #: repository is allowed
    allow_user_installation = Column(Boolean, nullable=False)
    #: boolean indicating whether installation of software to the system
    #: flatpak repository is allowed
    allow_system_installation = Column(Boolean, nullable=False)
    #: boolean indicating whether the user is an administrator (optional,
    #: defaults to false)
    is_administrator = Column(Boolean, nullable=False)
    #: boolean indicating whether this event is being submitted from initial
    #: setup or from an installed desktop (optional, defaults to false)
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
    """Any parental controls are enabled for the current user.

    Recorded every time the App Center checks for OS updates (using its
    ``eos-updater plugin``). This was chosen as a convenient regular event
    which happens inside the user session, rather than because of some deeper
    link to parental controls.

    No identifying details about the user or which parental controls are
    enabled. It’s intended to allow aggregate statistics about how widely
    parental controls are enabled (in any form).

    See `T28741 <https://phabricator.endlessm.com/T28741#810046>`_.

    :UUID name: ``GS_PARENTAL_CONTROLS_USAGE_EVENT`` in gnome-software

    .. versionadded:: 3.8.0

    """
    __tablename__ = 'parental_controls_enabled'
    __event_uuid__ = 'c227a817-808c-4fcb-b797-21002d17b69a'
    __payload_type__ = 'b'

    #: whether parental controls are enabled for this user
    enabled = Column(Boolean, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'enabled': payload.get_boolean(),
        }


class ProgramDumpedCore(SingularEvent):
    """A program crashes and ``systemd-coredump`` catches.

    We include the name of the program that crashed and the ostree commits of
    ostree repos on the system. We do not include programs that crashed within
    ``/home`` or ``/sysroot/home``.

    See `T18444 <https://phabricator.endlessm.com/T18444>`_.

    :UUID name: ``PROGRAM_DUMPED_CORE_EVENT`` in eos-metrics-instrumentation

    .. versionadded:: 3.2.5

    """
    __tablename__ = 'program_dumped_core'
    __event_uuid__ = 'ed57b607-4a56-47f1-b1e4-5dc3e74335ec'
    __payload_type__ = 'a{sv}'

    #: Dictionary of strign-to-variant containing the following keys:
    #:
    #: - ``binary``: the path to the binary on the system
    #: - ``signal``: what signal caused the program to crash
    #: - ``timestamp``: the timestamp the kernel reported the crash at
    #: - ``ostree_commit``: the hash of the OSTree commit
    #: - ``ostree_url``: the URL of the OSTree repository
    #: - ``app_ref``: optionally, the full Flatpak app ref,
    #:   e.g. ``app/net.sourceforge.ExtremeTuxRacer/x86_64/stable``
    #: - ``app_commit``: optionally, the hash of the OSTree commit for the crashed Flatpak app
    #: - ``app_url``: optionally, the URL of the Flatpak repository for the crashed app
    #: - ``runtime_ref``: optionally, the full Flatpak runtime ref used by the crashed app
    #: - ``runtime_commit``: optionally, the hash of the OSTree commit for the Flatpak runtime used
    #:   by the crashed app
    #: - ``runtime_url``: optionally, the URL of the Flatpak repository for the runtime used by the
    #:   crashed app
    info = Column(JSONB, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'info': payload.unpack()}


class RAMSize(SingularEvent):
    """RAM size at startup.

    See `T18445 <https://phabricator.endlessm.com/T18445>`_.

    :UUID name: ``RAM_SIZE_EVENT`` in eos-metrics-instrumentation

    .. versionadded:: 3.4.3

    """
    __tablename__ = 'ram_size'
    __event_uuid__ = 'aee94585-07a2-4483-a090-25abda650b12'
    __payload_type__ = 'u'

    #: total RAM size in mebibytes (2^20)
    total = Column(BigInteger, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'total': payload.get_uint32()}


class ShellAppAddedToDesktop(SingularEvent):
    """Shell application is added to desktop.

    :UUID name: ``SHELL_APP_ADDED_EVENT`` in gnome-shell

    .. note::

        Since 3.9.0 this metric is no longer recorded.
        See `T30661 <https://phabricator.endlessm.com/T30661>`_.

    .. versionadded:: 2.1.0

    """
    __tablename__ = 'shell_app_added_to_desktop'
    __event_uuid__ = '51640a4e-79aa-47ac-b7e2-d3106a06e129'
    __payload_type__ = 's'

    #: application ID
    app_id = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'app_id': payload.get_string()}


class ShellAppRemovedFromDesktop(SingularEvent):
    """Shell application is removed from desktop.

    :UUID name: ``SHELL_APP_REMOVED_EVENT`` in gnome-shell

    .. note::

        Since 3.9.0 this metric is no longer recorded.
        See `T30661 <https://phabricator.endlessm.com/T30661>`_.

    .. versionadded:: 2.1.0

    """
    __tablename__ = 'shell_app_removed_from_desktop'
    __event_uuid__ = '683b40a7-cac0-4f9a-994c-4b274693a0a0'
    __payload_type__ = 's'

    #: application ID
    app_id = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'app_id': payload.get_string()}


class UnderscanEnabled(SingularEvent):
    """Underscan is enabled on a monitor.

    :UUID name: ``UNDERSCAN_ENABLED`` in mutter

    .. versionadded:: 3.8.7

    """
    __tablename__ = 'underscan_enabled'
    __event_uuid__ = '304662c0-fdce-46b8-aa39-d1beb097efcd'
    __payload_type__ = None


class UpdaterBranchSelected(SingularEvent):
    """An eos-updater branch has been selected.

    :UUID name: ``EOS_UPDATER_METRIC_BRANCH_SELECTED`` in eos-updater

    .. versionadded:: 2.6.0

    """
    __tablename__ = 'updater_branch_selected'
    __event_uuid__ = '99f48aac-b5a0-426d-95f4-18af7d081c4e'
    __payload_type__ = '(sssb)'

    #: hardware vendor (e.g. "ASUStek, Inc.")
    hardware_vendor = Column(Unicode, nullable=False)
    #: hardware product (e.g. "Z1234")
    hardware_product = Column(Unicode, nullable=False)
    #: selected OSTree branch (e.g. "eos2/i386")
    ostree_branch = Column(Unicode, nullable=False)
    #: whether the device is on hold (it has been instructed by our server not
    #: to upgrade any further)
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
    """Failure of eos-updater or eos-updater-flatpak-installer for whatever reason.

    This can happen if an upgrade fails, or if installing required flatpaks fails.

    See `T29247 <https://phabricator.endlessm.com/T29247>`_.

    :UUID name: ``EOS_UPDATER_METRIC_FAILURE`` in eos-updater

    .. versionadded:: 2.6.0

    """
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
    """Total length of time the computer has been powered on and total number of boots.

    The difference with the system shutdown event is that this is sent
    periodically while the computer is up, not just at shutdown. This allows
    catching "dirty" shutdowns and makes it easier to estimate connectivity.

    See https://github.com/endlessm/eos-metrics-instrumentation/commit/8dfd1e5b9.

    :UUID name: ``UPTIME_EVENT`` in eos-metrics-instrumentation

    UUID was ``005096c4-9444-48c6-844b-6cb693c15235`` before 2.5.2.

    .. note::

        A serious bug that often prevented the boot count from being
        incremented was fixed in the 2.5.2 release.

    .. versionadded:: 2.5.0

    """
    __tablename__ = 'uptime'
    __event_uuid__ = '9af2cc74-d6dd-423f-ac44-600a6eee2d96'
    __payload_type__ = '(xx)'
    __ignore_empty_payload__ = True

    #: total uptime across all boots
    accumulated_uptime = Column(BigInteger, nullable=False)
    #: number of boots the computer has been through
    number_of_boots = Column(BigInteger, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'accumulated_uptime': payload.get_child_value(0).get_int64(),
            'number_of_boots': payload.get_child_value(1).get_int64(),
        }


class WindowsAppOpened(SingularEvent):
    """A user tries to open a ``.exe`` or ``.msi`` file.

    :UUID name: ``WINDOWS_APP_OPENED`` in eos-gates

    .. versionadded:: 2.1.5

    """
    __tablename__ = 'windows_app_opened'
    __event_uuid__ = 'cf09194a-3090-4782-ab03-87b2f1515aed'
    __payload_type__ = 'as'

    #: argv of the launched Windows application
    argv = Column(ARRAY(Unicode, dimensions=1), nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'argv': payload.unpack(),
        }


class WindowsLicenseTables(SingularEvent):
    """ACPI tables are present on the system, at startup.

    The tables we check for are MSDM and SLIC, which hold OEM Windows license
    information on newer and older systems respectively.

    We have not seen systems which have both tables, but they might exist in
    the wild and would appear with a value of 3. With this information,
    assuming Metrics Events is not sent, then we can distinguish:

    - SLIC/MSDM > 0 and no dual boot: Endless OS is the sole OS, PC came with Windows
    - SLIC/MSDM > 0 and dual boot: Endless OS installed alongside OEM Windows
    - SLIC/MSDM = 0 and no dual boot: Endless OS is the sole OS, PC came without Windows
    - SLIC/MSDM = 0 and dual boot: Dual-booting with a retail Windows

    See `T18296 <https://phabricator.endlessm.com/T18296>`_.

    :UUID name: ``WINDOWS_LICENSE_TABLES_EVENT`` in eos-metrics-instrumentation

    .. versionadded:: 3.2.0

    """
    __tablename__ = 'windows_license_tables'
    __event_uuid__ = 'ef74310f-7c7e-ca05-0e56-3e495973070a'
    __payload_type__ = 'u'

    # This comes in as a uint32, but PostgreSQL only has signed types so we need a BIGINT (int64)
    #: bitmask of which ACPI tables are found:
    #:
    #: - 0: no table found, system shipped without Windows
    #: - 1: MSDM table found, system shipped with newer Windows
    #: - 2: SLIC table found, system shipped with Vista-era Windows
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
    """An application opens and closes.

    By subtracting the time of closing from time of opening, we can tell how
    long an application has been open. This basically includes all applications
    of interest to non-developers.

    :UUID name: ``SHELL_APP_IS_OPEN_EVENT`` in gnome-shell

    .. versionadded:: 2.1.0

    """
    __tablename__ = 'shell_app_is_open'
    __event_uuid__ = 'b5e11a3d-13f8-4219-84fd-c9ba0bf3d1f0'
    __payload_type__ = 's'

    #: application ID
    app_id = Column(Unicode, nullable=False)
    #: number of seconds the application was open
    duration = Column(Float, default=default_time_duration, nullable=False)

    __table_args__ = (
        Index('ix_shell_app_is_open_app_id_started_at', 'app_id', 'started_at',
              postgresql_ops={'app_id': 'varchar_pattern_ops'}),
    )

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'app_id': payload.get_string()}


class UserIsLoggedIn(SequenceEvent):
    """A user logs in and logs out to Endless OS.

    As of 2.1.2 we also records which user logged in. This is still anonymous
    data, so we only record an arbitrary number (the user ID), but we can
    discover (among other things) how many different users use the computer
    that way.

    :UUID name: ``USER_IS_LOGGED_IN`` in eos-metrics-instrumentation (since 2.1.2)

    UUID was called ``EMTR_EVENT_USER_IS_LOGGED_IN``
    (``ab839fd2-a927-456c-8c18-f1136722666b``) before 2.1.2.

    .. note::

        A serious bug that often prevented this event from being recorded was
        introduced in 2.4.0 and fixed in 2.5.1.

    .. versionadded:: 2.1.0

    """
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
