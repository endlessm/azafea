# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from typing import Any, Dict

from gi.repository import GLib

import pytest

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, Unicode


def test_singular_registry():
    from azafea.event_processors.endless.metrics.v2.model import (
        SINGULAR_EVENT_MODELS, SingularEvent)

    class TestSingularEvent(SingularEvent):
        __tablename__ = 'test_singular_v2'
        __event_uuid__ = '00000000-0000-0000-0000-000000000000'

    assert SINGULAR_EVENT_MODELS['00000000-0000-0000-0000-000000000000'] == TestSingularEvent


def test_aggregate_registry():
    from azafea.event_processors.endless.metrics.v2.model import (
        AGGREGATE_EVENT_MODELS, AggregateEvent)

    class TestAggregateEvent(AggregateEvent):
        __tablename__ = 'test_aggregate_v2'
        __event_uuid__ = '00000000-0000-0000-0000-000000000000'

    assert AGGREGATE_EVENT_MODELS['00000000-0000-0000-0000-000000000000'] == TestAggregateEvent


def test_sequence_registry():
    from azafea.event_processors.endless.metrics.v2.model import (
        SEQUENCE_EVENT_MODELS, SequenceEvent)

    class TestSequenceEvent(SequenceEvent):
        __tablename__ = 'test_sequence_v2'
        __event_uuid__ = '00000000-0000-0000-0000-000000000000'

    assert SEQUENCE_EVENT_MODELS['00000000-0000-0000-0000-000000000000'] == TestSequenceEvent


def test_new_event_no_payload():
    from azafea.event_processors.endless.metrics.v2.model import SingularEvent

    class TestEventNoPayload(SingularEvent):
        __tablename__ = 'test_singular_no_payload_v2'
        __event_uuid__ = '00000000-0000-0000-0000-000000000000'
        __payload_type__ = None

    payload = GLib.Variant('mv', None)
    TestEventNoPayload(payload=payload)


def test_new_event_with_payload():
    from azafea.event_processors.endless.metrics.v2.model import SingularEvent

    class TestEventWithPayload(SingularEvent):
        __tablename__ = 'test_singular_with_payload_v2'
        __event_uuid__ = '00000000-0000-0000-0000-000000000000'
        __payload_type__ = '(is)'

        the_int = Column(Integer, nullable=False)
        the_str = Column(Unicode, nullable=False)

        @staticmethod
        def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
            return {
                'the_int': payload.get_child_value(0).get_int32(),
                'the_str': payload.get_child_value(1).get_string(),
            }

    payload = GLib.Variant('mv', GLib.Variant('(is)', (43, 'foo')))
    event = TestEventWithPayload(payload=payload)
    assert event.the_int == 43
    assert event.the_str == 'foo'


def test_new_event_no_payload_but_payload_given(capfd):
    from azafea.logging import setup_logging
    from azafea.event_processors.endless.metrics.v2.model import SingularEvent

    setup_logging(verbose=False)

    class TestEventNoPayloadButPayloadGiven(SingularEvent):
        __tablename__ = 'test_singular_no_payload_but_payload_given_v2'
        __event_uuid__ = '00000000-0000-0000-0000-000000000000'
        __payload_type__ = None

    payload = GLib.Variant('mv', GLib.Variant('i', 1))
    TestEventNoPayloadButPayloadGiven(payload=payload)

    capture = capfd.readouterr()
    assert ('Metric event 00000000-0000-0000-0000-000000000000 takes no payload, '
            'but got <1>') in capture.err


def test_new_event_no_payload_given():
    from azafea.event_processors.endless.metrics.v2.model import EmptyPayloadError, SingularEvent

    class TestEventNoPayloadGiven(SingularEvent):
        __tablename__ = 'test_singular_no_payload_given_v2'
        __event_uuid__ = '00000000-0000-0000-0000-000000000000'
        __payload_type__ = 'i'

    payload = GLib.Variant('mv', None)

    with pytest.raises(EmptyPayloadError) as excinfo:
        TestEventNoPayloadGiven(payload=payload)

    assert ('Metric event 00000000-0000-0000-0000-000000000000 needs a i payload, '
            'but got none') in str(excinfo.value)


def test_new_event_wrong_payload_given():
    from azafea.event_processors.endless.metrics.v2.model import SingularEvent, WrongPayloadError

    class TestEventWrongPayloadGiven(SingularEvent):
        __tablename__ = 'test_singular_wrong_payload_given_v2'
        __event_uuid__ = '00000000-0000-0000-0000-000000000000'
        __payload_type__ = 'i'

    payload = GLib.Variant('mv', GLib.Variant('s', 'foo'))

    with pytest.raises(WrongPayloadError) as excinfo:
        TestEventWrongPayloadGiven(payload=payload)

    assert ('Metric event 00000000-0000-0000-0000-000000000000 needs a i payload, '
            "but got 'foo' (s)") in str(excinfo.value)


def test_new_unknown_event():
    from azafea.event_processors.endless.metrics.v2.model import UnknownEvent

    class TestUnknownEvent(UnknownEvent):
        __tablename__ = 'test_unknown_v2'

    payload = GLib.Variant('mv', GLib.Variant('i', 43))
    event = TestUnknownEvent(payload=payload)
    assert event.payload_data == payload.get_data_as_bytes().get_data()


@pytest.mark.parametrize('event_model_name, payload, expected_attrs', [
    ('CacheIsCorrupt', None, {}),
    ('CacheMetadataIsCorrupt', None, {}),
    (
        'ControlCenterAutomaticUpdates',
        GLib.Variant('(bbbv)', (True, False, False,
                                GLib.Variant.parse(None,
                                                   "('Mogwai tariff', uint16 2, <('System Tariff', [(uint64 0, uint64 253402300799, 'UTC', 'UTC', uint16 0, uint32 0, uint64 0), (79200, 108000, 'Europe/London', 'Europe/London', 2, 1, 18446744073709551615)])>)",  # noqa: E501
                                                   None, None))),
        {
            'allow_downloads_when_metered': True,
            'automatic_updates_enabled': False,
            'tariff_enabled': False,
            'tariff_variant': (
                'Mogwai tariff', 2, ('System Tariff', [
                    (0, 253402300799, 'UTC', 'UTC', 0, 0, 0),
                    (79200, 108000, 'Europe/London', 'Europe/London', 2, 1, 18446744073709551615),
                ])
            ),
        }
    ),
    (
        'ControlCenterAutomaticUpdates',
        GLib.Variant('(bbbv)', (True, True, False,
                                GLib.Variant.parse(None,
                                                   "('Mogwai tariff', uint16 2, <('System Tariff', [(uint64 0, uint64 253402300799, 'UTC', 'UTC', uint16 0, uint32 0, uint64 0), (79200, 108000, 'Europe/London', 'Europe/London', 2, 1, 18446744073709551615)])>)",  # noqa: E501
                                                   None, None))),
        {
            'allow_downloads_when_metered': True,
            'automatic_updates_enabled': True,
            'tariff_enabled': False,
            'tariff_variant': (
                'Mogwai tariff', 2, ('System Tariff', [
                    (0, 253402300799, 'UTC', 'UTC', 0, 0, 0),
                    (79200, 108000, 'Europe/London', 'Europe/London', 2, 1, 18446744073709551615),
                ])
            ),
        }
    ),
    (
        'ControlCenterAutomaticUpdates',
        GLib.Variant('(bbbv)', (True, True, True,
                                GLib.Variant.parse(None,
                                                   "('Mogwai tariff', uint16 2, <('System Tariff', [(uint64 0, uint64 253402300799, 'UTC', 'UTC', uint16 0, uint32 0, uint64 0), (79200, 115200, 'Europe/London', 'Europe/London', 2, 1, 18446744073709551615)])>)",  # noqa: E501
                                                   None, None))),
        {
            'allow_downloads_when_metered': True,
            'automatic_updates_enabled': True,
            'tariff_enabled': True,
            'tariff_variant': (
                'Mogwai tariff', 2, ('System Tariff', [
                    (0, 253402300799, 'UTC', 'UTC', 0, 0, 0),
                    (79200, 115200, 'Europe/London', 'Europe/London', 2, 1, 18446744073709551615),
                ])
            ),
        }
    ),
    ('ControlCenterPanelOpened', GLib.Variant('s', 'privacy'), {'name': 'privacy'}),
    (
        'CPUInfo',
        GLib.Variant('a(sqd)', [('Intel(R) Core(TM) i7-5600U CPU @ 2.60GHz', 4, 2600.0)]),
        {
            'info': [{
                'model': 'Intel(R) Core(TM) i7-5600U CPU @ 2.60GHz',
                'cores': 4,
                'max_frequency': 2600.0,
            }]
        }
    ),
    (
        'DiscoveryFeedClicked',
        GLib.Variant('a{ss}', {'app_id': 'org.gnome.Totem', 'content_type': 'knowledge_video'}),
        {'info': {'app_id': 'org.gnome.Totem', 'content_type': 'knowledge_video'}}
    ),
    (
        'DiscoveryFeedClosed',
        GLib.Variant('a{ss}', {'closed_by': 'buttonclose', 'time_open': '123'}),
        {'info': {'closed_by': 'buttonclose', 'time_open': '123'}}
    ),
    (
        'DiscoveryFeedOpened',
        GLib.Variant('a{ss}', {'opened_by': 'shell_button', 'language': 'fr_FR.UTF-8'}),
        {'info': {'opened_by': 'shell_button', 'language': 'fr_FR.UTF-8'}}
    ),
    ('DiskSpaceExtra', GLib.Variant('(uuu)', (30, 10, 20)), {'total': 30, 'used': 10, 'free': 20}),
    ('DiskSpaceSysroot', GLib.Variant('(uuu)', (5, 3, 2)), {'total': 5, 'used': 3, 'free': 2}),
    ('DualBootBooted', None, {}),
    (
        'EndlessApplicationUnmaximized',
        GLib.Variant('s', 'org.gnome.Calendar'),
        {'app_id': 'org.gnome.Calendar'}
    ),
    ('EnteredDemoMode', None, {}),
    (
        'HackClubhouseAchievement',
        GLib.Variant('(ss)', ('id', 'name')),
        {'achievement_id': 'id', 'achievement_name': 'name'}
    ),
    (
        'HackClubhouseAchievementPoints',
        GLib.Variant('(sii)', ('skillset', 0, 1)),
        {'skillset': 'skillset', 'points': 0, 'new_points': 1}
    ),
    ('HackClubhouseChangePage', GLib.Variant('s', 'page'), {'page': 'page'}),
    ('HackClubhouseEnterPathway', GLib.Variant('s', 'pathway'), {'pathway': 'pathway'}),
    ('HackClubhouseMode', GLib.Variant('b', True), {'active': True}),
    (
        'HackClubhouseNewsQuestLink',
        GLib.Variant('(ss)', ('character', 'quest')),
        {'character': 'character', 'quest': 'quest'}
    ),
    (
        'HackClubhouseProgress',
        GLib.Variant('a{sv}', {
            'complete': GLib.Variant('b', True),
            'quest': GLib.Variant('s', 'quest'),
            'pathways': GLib.Variant('av', [
                GLib.Variant('s', 'pathway1'),
                GLib.Variant('s', 'pathway2'),
            ]),
            'progress': GLib.Variant('d', 100.0),
        }),
        {
            'complete': True,
            'quest': 'quest',
            'pathways': ['pathway1', 'pathway2'],
            'progress': 100.0,
        }
    ),
    ('ImageVersion', GLib.Variant('s', 'image'), {'image_id': 'image'}),
    (
        'LaunchedEquivalentExistingFlatpak',
        GLib.Variant('(sas)', ('org.glimpse_editor.Glimpse', ['photoshop.exe'])),
        {'replacement_app_id': 'org.glimpse_editor.Glimpse', 'argv': ['photoshop.exe']}
    ),
    (
        'LaunchedEquivalentInstallerForFlatpak',
        GLib.Variant('(sas)', ('org.glimpse_editor.Glimpse', ['photoshop.exe'])),
        {'replacement_app_id': 'org.glimpse_editor.Glimpse', 'argv': ['photoshop.exe']}
    ),
    (
        'LaunchedExistingFlatpak',
        GLib.Variant('(sas)', ('org.gnome.Calendar', ['gnome-calendar.deb'])),
        {'replacement_app_id': 'org.gnome.Calendar', 'argv': ['gnome-calendar.deb']}
    ),
    (
        'LaunchedInstallerForFlatpak',
        GLib.Variant('(sas)', ('org.gnome.Calendar', ['gnome-calendar.deb'])),
        {'replacement_app_id': 'org.gnome.Calendar', 'argv': ['gnome-calendar.deb']}
    ),
    (
        'LinuxPackageOpened',
        GLib.Variant('as', ['gnome-calendar.deb']),
        {'argv': ['gnome-calendar.deb']}
    ),
    ('LiveUsbBooted', None, {}),
    (
        'Location',
        GLib.Variant('(ddbdd)', (5.4, 6.5, False, 7.6, 8.7)),
        {'latitude': 5.4, 'longitude': 6.5, 'altitude': None, 'accuracy': 8.7}
    ),
    (
        'Location',
        GLib.Variant('(ddbdd)', (1.0, 2.1, True, 3.2, 4.3)),
        {'latitude': 1.0, 'longitude': 2.1, 'altitude': 3.2, 'accuracy': 4.3}
    ),
    (
        'LocationLabel',
        GLib.Variant('a{ss}', {'city': 'City', 'state': 'State', 'facility': 'Facility'}),
        {'info': {'city': 'City', 'state': 'State', 'facility': 'Facility'}}
    ),
    (
        'LocationLabel',
        GLib.Variant('a{ss}', {'city': '', 'state': '', 'facility': 'Facility'}),
        {'info': {'facility': 'Facility'}}
    ),
    (
        'MissingCodec',
        GLib.Variant('(ssssa{sv})', (
            '1.16.0',
            'Videos',
            'decoder',
            'audio/mp3',
            {
                'mpegaudioversion': GLib.Variant('i', 1),
                'mpegversion': GLib.Variant('i', 1),
                'layer': GLib.Variant('u', 3),
            },
        )),
        {
            'gstreamer_version': '1.16.0',
            'app_name': 'Videos',
            'type': 'decoder',
            'name': 'audio/mp3',
            'extra_info': {
                'mpegaudioversion': 1,
                'mpegversion': 1,
                'layer': 3,
            },
        }
    ),
    ('NetworkId', GLib.Variant('u', 123456), {'network_id': 123456}),
    (
        'OSVersion',
        GLib.Variant('(sss)', ('Endless', '3.5.3', 'obsolete and ignored')),
        {'version': '3.5.3'}
    ),
    (
        'OSVersion',
        GLib.Variant('(sss)', ('"Endless"', '"3.5.3"', 'obsolete and ignored')),
        {'version': '3.5.3'}
    ),
    (
        'ParentalControlsBlockedFlatpakInstall',
        GLib.Variant('s', 'com.realm667.WolfenDoom_Blade_of_Agony'),
        {'app': 'com.realm667.WolfenDoom_Blade_of_Agony'}
    ),
    (
        'ParentalControlsBlockedFlatpakRun',
        GLib.Variant('s', 'com.realm667.WolfenDoom_Blade_of_Agony'),
        {'app': 'com.realm667.WolfenDoom_Blade_of_Agony'}
    ),
    (
        'ParentalControlsChanged',
        GLib.Variant('a{sv}', {
            'AppFilter': GLib.Variant('(bas)', (False, [
                'org.libreoffice.LibreOffice',
                'org.gnome.Totem',
            ])),
            'OarsFilter': GLib.Variant('(sa{ss})', ('oars-1.0', {
                'violence-bloodshed': 'mild',
                'violence-realistic': 'intense',
            })),
            'AllowUserInstallation': GLib.Variant('b', True),
            'AllowSystemInstallation': GLib.Variant('b', True),
            'IsAdministrator': GLib.Variant('b', True),
            'IsInitialSetup': GLib.Variant('b', True),
        }),
        {
            'app_filter_is_whitelist': False,
            'app_filter': [
                'org.libreoffice.LibreOffice',
                'org.gnome.Totem',
            ],
            'oars_filter': {
                'violence-bloodshed': 'mild',
                'violence-realistic': 'intense',
            },
            'allow_user_installation': True,
            'allow_system_installation': True,
            'is_administrator': True,
            'is_initial_setup': True,
        }
    ),
    (
        'ParentalControlsChanged',
        GLib.Variant('a{sv}', {
            'AppFilter': GLib.Variant('(bas)', (True, [])),
            'OarsFilter': GLib.Variant('(sa{ss})', ('oars-1.1', {})),
            'AllowUserInstallation': GLib.Variant('b', False),
            'AllowSystemInstallation': GLib.Variant('b', False),
            'UnexpectedKey': GLib.Variant('s', 'should be ignored'),
        }),
        {
            'app_filter_is_whitelist': True,
            'app_filter': [],
            'oars_filter': {},
            'allow_user_installation': False,
            'allow_system_installation': False,
        }
    ),
    (
        'ParentalControlsChanged',
        GLib.Variant('a{sv}', {
            'AllowSystemInstallation': GLib.Variant('b', True),
            'AllowUserInstallation': GLib.Variant('b', True),
            'IsAdministrator': GLib.Variant('b', True),
            'OarsFilter': GLib.Variant('(sa{ss})', ('oars-1.1', {})),
            'AppFilter': GLib.Variant('(bas)', (False, [])),
            'IsInitialSetup': GLib.Variant('b', False),
        }),
        {
            'app_filter_is_whitelist': False,
            'app_filter': [],
            'oars_filter': {},
            'allow_user_installation': True,
            'allow_system_installation': True,
        }
    ),
    (
        'ParentalControlsChanged',
        GLib.Variant('a{sv}', {
            'AllowSystemInstallation': GLib.Variant('b', False),
            'AllowUserInstallation': GLib.Variant('b', False),
            'IsAdministrator': GLib.Variant('b', False),
            'OarsFilter': GLib.Variant('(sa{ss})', ('oars-1.1', {})),
            'AppFilter': GLib.Variant('(bas)', (False, [
                'app/com.hack_computer.ProjectLibrary/x86_64/eos3',
                'app/com.hack_computer.Clubhouse/x86_64/eos3',
                'app/com.hack_computer.Sidetrack/x86_64/eos3',
                'app/org.libreoffice.LibreOffice/x86_64/stable',
                'x-scheme-handler/http',
            ])),
            'IsInitialSetup': GLib.Variant('b', False),
        }),
        {
            'app_filter_is_whitelist': False,
            'app_filter': [
                'app/com.hack_computer.ProjectLibrary/x86_64/eos3',
                'app/com.hack_computer.Clubhouse/x86_64/eos3',
                'app/com.hack_computer.Sidetrack/x86_64/eos3',
                'app/org.libreoffice.LibreOffice/x86_64/stable',
                'x-scheme-handler/http',
            ],
            'oars_filter': {},
            'allow_user_installation': False,
            'allow_system_installation': False,
            'is_administrator': False,
            'is_initial_setup': False,
        }
    ),
    (
        'ParentalControlsEnabled',
        GLib.Variant('b', False),
        {'enabled': False}
    ),
    (
        'ProgramDumpedCore',
        GLib.Variant('a{sv}', {
            'binary': GLib.Variant('s', '/app/bin/evolution'),
            'signal': GLib.Variant('u', 11),
        }),
        {'info': {'binary': '/app/bin/evolution', 'signal': 11}}
    ),
    ('RAMSize', GLib.Variant('u', 32000), {'total': 32000}),
    (
        'ShellAppAddedToDesktop',
        GLib.Variant('s', 'org.gnome.Calendar'),
        {'app_id': 'org.gnome.Calendar'}
    ),
    (
        'ShellAppRemovedFromDesktop',
        GLib.Variant('s', 'org.gnome.Evolution'),
        {'app_id': 'org.gnome.Evolution'}
    ),
    ('UnderscanEnabled', None, {}),
    (
        'UpdaterBranchSelected',
        GLib.Variant('(sssb)', (
            'Asustek Computer Inc.',
            'To Be Filled By O.E.M.',
            'os/eos/amd64/eos3',
            False
        )),
        {
            'hardware_vendor': 'ASUS',
            'hardware_product': 'To Be Filled By O.E.M.',
            'ostree_branch': 'os/eos/amd64/eos3',
            'on_hold': False,
        }
    ),
    (
        'UpdaterFailure',
        GLib.Variant('(ss)', ('eos-updater', 'Oh no!')),
        {
            'component': 'eos-updater',
            'error_message': 'Oh no!',
        }
    ),
    ('Uptime', GLib.Variant('(xx)', (2, 1)), {'accumulated_uptime': 2, 'number_of_boots': 1}),
    ('WindowsAppOpened', GLib.Variant('as', ['photoshop.exe']), {'argv': ['photoshop.exe']}),
    ('WindowsLicenseTables', GLib.Variant('u', 0), {'tables': 0}),
    (
        'CacheHasInvalidElements',
        GLib.Variant('(tt)', (10, 1500)),
        {'number_of_valid_elements': 10, 'number_of_bytes_read': 1500},
    ),
    (
        'CacheHasInvalidElements',
        GLib.Variant('(tt)', (10, 10**19)),
        {'number_of_valid_elements': 10, 'number_of_bytes_read': GLib.MAXINT64},
    ),
    (
        'StartupFinished',
        GLib.Variant('(tttttt)', (10, 15, 20, 25, 50, 120)),
        {
            'firmware': 10,
            'loader': 15,
            'kernel': 20,
            'initrd': 25,
            'userspace': 50,
            'total': 120,
        },
    ),
    (
        'StartupFinished',
        GLib.Variant('(tttttt)', (0, 0, 0, 10, 10**19, 10 + 10**19)),
        {
            'firmware': 0,
            'loader': 0,
            'kernel': 0,
            'initrd': 10,
            'userspace': GLib.MAXINT64,
            'total': GLib.MAXINT64,
        },
    ),
])
def test_singular_event(event_model_name, payload, expected_attrs):
    from azafea.event_processors.endless.metrics.v2 import model

    event_model = getattr(model, event_model_name)
    maybe_payload = GLib.Variant('mv', payload)

    event = event_model(payload=maybe_payload)

    for attr_name, attr_value in expected_attrs.items():
        assert getattr(event, attr_name) == attr_value


def test_invalid_hack_clubhouse_progress_event():
    from azafea.event_processors.endless.metrics.v2.model import HackClubhouseProgress

    # Make an invalid payload with missing keys
    payload = GLib.Variant('mv', GLib.Variant('a{sv}', {'complete': GLib.Variant('b', True)}))

    with pytest.raises(ValueError) as excinfo:
        HackClubhouseProgress(payload)

    assert str(excinfo.value) == ('Metric event 3a037364-9164-4b42-8c07-73bcc00902de needs an '
                                  '"a{sv}" payload with certain keys, but some were missing: got '
                                  "['complete']")


def test_hack_clubhouse_progress_event_with_unknown_key():
    # Additional event attributes passed to the constructor are ignored by our base model, but for
    # this specific event the code parsing the payload does its own ignoring as well, so let's test
    # it to be sure.
    from azafea.event_processors.endless.metrics.v2.model import HackClubhouseProgress

    # Make an invalid payload with extra keys
    payload = GLib.Variant('mv', GLib.Variant('a{sv}', {
        'progress': GLib.Variant('d', 95.3),
        'complete': GLib.Variant('b', False),
        'quest': GLib.Variant('s', 'quest'),
        'pathways': GLib.Variant('av', [
            GLib.Variant('s', 'pathway2'),
            GLib.Variant('s', 'pathway1'),
        ]),
        'unknown': GLib.Variant('s', 'ignored'),
    }))

    event = HackClubhouseProgress(payload)

    assert not event.complete
    assert event.quest == 'quest'
    assert event.pathways == ['pathway2', 'pathway1']
    assert event.progress == 95.3
    assert not hasattr(event, 'unknown')


def test_valid_linux_package_opened_single_string():
    from azafea.event_processors.endless.metrics.v2.model import LinuxPackageOpened

    payload = GLib.Variant('mv', GLib.Variant('s', 'gnome-calendar.deb'))
    lpo = LinuxPackageOpened(payload)
    assert lpo.argv == ['gnome-calendar.deb']


def test_valid_linux_package_opened_array_string():
    from azafea.event_processors.endless.metrics.v2.model import LinuxPackageOpened

    payload = GLib.Variant('mv', GLib.Variant('as', ['gnome-calendar.deb']))
    lpo = LinuxPackageOpened(payload)
    assert lpo.argv == ['gnome-calendar.deb']


def test_empty_payload_linux_package_opened():
    from azafea.event_processors.endless.metrics.v2.model import (
        EmptyPayloadError, LinuxPackageOpened
    )

    payload = GLib.Variant('mv', None)

    with pytest.raises(EmptyPayloadError) as excinfo:
        LinuxPackageOpened(payload)

    assert ('Metric event 0bba3340-52e3-41a2-854f-e6ed36621379 needs a as payload, '
            'but got none') in str(excinfo.value)


def test_invalid_payload_linux_package_opened():
    from azafea.event_processors.endless.metrics.v2.model import (
        WrongPayloadError, LinuxPackageOpened
    )

    payload = GLib.Variant('mv', GLib.Variant('x', 100000))

    with pytest.raises(WrongPayloadError) as excinfo:
        LinuxPackageOpened(payload)

    assert ('Metric event 0bba3340-52e3-41a2-854f-e6ed36621379 needs a as payload, '
            "but got int64 100000 (x)") in str(excinfo.value)


def test_invalid_parental_controls_changed_event():
    from azafea.event_processors.endless.metrics.v2.model import ParentalControlsChanged

    # Make an invalid payload with missing keys
    payload = GLib.Variant('mv', GLib.Variant('a{sv}', {
        'AllowUserInstallation': GLib.Variant('b', False),
        'AllowSystemInstallation': GLib.Variant('b', False),
        'UnexpectedKey': GLib.Variant('s', 'should be ignored'),
    }))

    with pytest.raises(ValueError) as excinfo:
        ParentalControlsChanged(payload)

    assert str(excinfo.value) == ('Metric event 449ec188-cb7b-45d3-a0ed-291d943b9aa6 needs an '
                                  '"a{sv}" payload with certain keys, but some were missing: got '
                                  "{'AllowUserInstallation': <false>, 'AllowSystemInstallation': "
                                  "<false>, 'UnexpectedKey': <'should be ignored'>}")


def test_invalid_parental_controls_changed_oars_event():
    from azafea.event_processors.endless.metrics.v2.model import ParentalControlsChanged

    # Make an invalid payload with an unknown OARS filter type
    payload = GLib.Variant('mv', GLib.Variant('a{sv}', {
        'AppFilter': GLib.Variant('(bas)', (True, [])),
        'OarsFilter': GLib.Variant('(sa{ss})', ('not right', {})),
        'AllowUserInstallation': GLib.Variant('b', False),
        'AllowSystemInstallation': GLib.Variant('b', False),
    }))

    with pytest.raises(ValueError) as excinfo:
        ParentalControlsChanged(payload)

    assert str(excinfo.value) == ('Metric event 449ec188-cb7b-45d3-a0ed-291d943b9aa6 needs an '
                                  '"OarsFilter" key in oars-1.0 or oars-1.1 format, but '
                                  'actually got '
                                  "{'AppFilter': <(true, @as [])>, 'OarsFilter': <('not right', "
                                  "@a{ss} {})>, 'AllowUserInstallation': <false>, "
                                  "'AllowSystemInstallation': <false>}")


def test_empty_location_label():
    from azafea.event_processors.endless.metrics.v2.model import EmptyPayloadError, LocationLabel

    # Make an invalid payload with missing keys
    payload = GLib.Variant('mv', GLib.Variant('a{ss}', {'empty': ''}))

    with pytest.raises(EmptyPayloadError) as excinfo:
        LocationLabel(payload)

    assert str(excinfo.value) == 'Location label event received with no data.'


@pytest.mark.parametrize('event_model_name, payload, expected_attrs', [
    ('ShellAppIsOpen', GLib.Variant('s', 'org.gnome.Calendar'), {'app_id': 'org.gnome.Calendar'}),
    ('UserIsLoggedIn', GLib.Variant('u', 1000), {'logged_in_user_id': 1000}),
])
def test_sequence_event(event_model_name, payload, expected_attrs):
    from azafea.event_processors.endless.metrics.v2 import model

    event_model = getattr(model, event_model_name)
    maybe_payload = GLib.Variant('mv', payload)

    event = event_model(payload=maybe_payload)

    for attr_name, attr_value in expected_attrs.items():
        assert getattr(event, attr_name) == attr_value
