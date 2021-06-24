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
    from azafea.event_processors.endless.metrics.v3.model import (
        SINGULAR_EVENT_MODELS, SingularEvent)

    class TestSingularEvent(SingularEvent):
        __tablename__ = 'test_singular'
        __event_uuid__ = '00000000-0000-0000-0000-000000000000'

    assert SINGULAR_EVENT_MODELS['00000000-0000-0000-0000-000000000000'] == TestSingularEvent


def test_aggregate_registry():
    from azafea.event_processors.endless.metrics.v3.model import (
        AGGREGATE_EVENT_MODELS, AggregateEvent)

    class TestAggregateEvent(AggregateEvent):
        __tablename__ = 'test_aggregate'
        __event_uuid__ = '00000000-0000-0000-0000-000000000000'

    assert AGGREGATE_EVENT_MODELS['00000000-0000-0000-0000-000000000000'] == TestAggregateEvent


def test_new_event_no_payload():
    from azafea.event_processors.endless.metrics.v3.model import SingularEvent

    class TestEventNoPayload(SingularEvent):
        __tablename__ = 'test_singular_no_payload'
        __event_uuid__ = '00000000-0000-0000-0000-000000000000'
        __payload_type__ = None

    payload = GLib.Variant('mv', None)
    TestEventNoPayload(payload=payload)


def test_new_event_with_payload():
    from azafea.event_processors.endless.metrics.v3.model import SingularEvent

    class TestEventWithPayload(SingularEvent):
        __tablename__ = 'test_singular_with_payload'
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
    from azafea.event_processors.endless.metrics.v3.model import SingularEvent

    setup_logging(verbose=False)

    class TestEventNoPayloadButPayloadGiven(SingularEvent):
        __tablename__ = 'test_singular_no_payload_but_payload_given'
        __event_uuid__ = '00000000-0000-0000-0000-000000000000'
        __payload_type__ = None

    payload = GLib.Variant('mv', GLib.Variant('i', 1))
    TestEventNoPayloadButPayloadGiven(payload=payload)

    capture = capfd.readouterr()
    assert ('Metric event 00000000-0000-0000-0000-000000000000 takes no payload, '
            'but got <1>') in capture.err


def test_new_event_no_payload_given():
    from azafea.event_processors.endless.metrics.v3.model import EmptyPayloadError, SingularEvent

    class TestEventNoPayloadGiven(SingularEvent):
        __tablename__ = 'test_singular_no_payload_given'
        __event_uuid__ = '00000000-0000-0000-0000-000000000000'
        __payload_type__ = 'i'

    payload = GLib.Variant('mv', None)

    with pytest.raises(EmptyPayloadError) as excinfo:
        TestEventNoPayloadGiven(payload=payload)

    assert ('Metric event 00000000-0000-0000-0000-000000000000 needs a i payload, '
            'but got none') in str(excinfo.value)


def test_new_event_wrong_payload_given():
    from azafea.event_processors.endless.metrics.v3.model import SingularEvent, WrongPayloadError

    class TestEventWrongPayloadGiven(SingularEvent):
        __tablename__ = 'test_singular_wrong_payload_given'
        __event_uuid__ = '00000000-0000-0000-0000-000000000000'
        __payload_type__ = 'i'

    payload = GLib.Variant('mv', GLib.Variant('s', 'foo'))

    with pytest.raises(WrongPayloadError) as excinfo:
        TestEventWrongPayloadGiven(payload=payload)

    assert ('Metric event 00000000-0000-0000-0000-000000000000 needs a i payload, '
            "but got 'foo' (s)") in str(excinfo.value)


def test_new_unknown_event():
    from azafea.event_processors.endless.metrics.v3.model import UnknownEvent

    class TestUnknownEvent(UnknownEvent):
        __tablename__ = 'test_unknown'

    payload = GLib.Variant('mv', GLib.Variant('i', 43))
    event = TestUnknownEvent(payload=payload)
    assert event.payload_data == payload.get_data_as_bytes().get_data()


@pytest.mark.parametrize('event_model_name, payload, expected_attrs', [
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
    (
        'UpdaterFailure',
        GLib.Variant('(ss)', ('eos-updater', 'Oh no!')),
        {
            'component': 'eos-updater',
            'error_message': 'Oh no!',
        }
    ),
    ('WindowsAppOpened', GLib.Variant('as', ['photoshop.exe']), {'argv': ['photoshop.exe']}),
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
    from azafea.event_processors.endless.metrics.v3 import model

    event_model = getattr(model, event_model_name)
    maybe_payload = GLib.Variant('mv', payload)

    event = event_model(payload=maybe_payload)

    for attr_name, attr_value in expected_attrs.items():
        assert getattr(event, attr_name) == attr_value


def test_invalid_parental_controls_changed_event():
    from azafea.event_processors.endless.metrics.v3.model import ParentalControlsChanged

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
    from azafea.event_processors.endless.metrics.v3.model import ParentalControlsChanged

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