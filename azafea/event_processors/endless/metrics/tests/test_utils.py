# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from datetime import datetime, timezone
from gi.repository import GLib

import pytest


def test_get_asv_dict():
    from azafea.event_processors.endless.metrics.utils import get_asv_dict

    variant = GLib.Variant('a{sv}', {
        'b': GLib.Variant('b', True),
        'd': GLib.Variant('d', 10.01),
        'i': GLib.Variant('i', -10),
        'n': GLib.Variant('n', -1),
        'x': GLib.Variant('x', -1985),
        'u': GLib.Variant('u', 10),
        'q': GLib.Variant('q', 1),
        't': GLib.Variant('t', 1985),
        's': GLib.Variant('s', '🎂️'),
        'as': GLib.Variant('as', ['🌬️', '🎂️']),
    })
    assert get_asv_dict(variant) == {
        'b': True,
        'd': 10.01,
        'i': -10,
        'n': -1,
        'x': -1985,
        'u': 10,
        'q': 1,
        't': 1985,
        's': '🎂️',
        'as': ['🌬️', '🎂️'],
    }


@pytest.mark.parametrize('type_string, value', [
    ('y', b'n'),
    ('h', 512),
    ('o', '/path/to/nope'),
    ('g', 'no'),
    ('mi', None),
    ('mv', GLib.Variant('i', 10)),
    ('(ii)', (10, 1)),
    ('a{sv}', {'nope': GLib.Variant('s', 'nope')}),
])
def test_get_asv_dict_not_implemented(type_string, value):
    from azafea.event_processors.endless.metrics.utils import get_asv_dict

    variant = GLib.Variant('a{sv}', {
        'foo': GLib.Variant(type_string, value),
    })

    with pytest.raises(NotImplementedError) as excinfo:
        get_asv_dict(variant)

    assert f"Can't unpack {type_string!r} variant in {variant}" in str(excinfo.value)


def test_get_bytes():
    from azafea.event_processors.endless.metrics.utils import get_bytes

    variant = GLib.Variant('ay', b'some bytes')
    assert get_bytes(variant) == b'some bytes'


def test_get_child_values():
    from azafea.event_processors.endless.metrics.utils import get_child_values

    variant = GLib.Variant('ay', b'123')
    assert list(get_child_values(variant)) == [
        GLib.Variant('y', b'1'),
        GLib.Variant('y', b'2'),
        GLib.Variant('y', b'3'),
    ]


def test_get_strings():
    from azafea.event_processors.endless.metrics.utils import get_strings

    variant = GLib.Variant('as', ['foo', 'bar'])
    assert get_strings(variant) == ['foo', 'bar']


@pytest.mark.parametrize('variant', [
    GLib.Variant('v', GLib.Variant('i', 41)),
    GLib.Variant('v', GLib.Variant('v', GLib.Variant('i', 41))),
    GLib.Variant('v', GLib.Variant('v', GLib.Variant('v', GLib.Variant('i', 41)))),
])
def test_get_variant(variant):
    from azafea.event_processors.endless.metrics.utils import get_variant

    assert get_variant(variant) == GLib.Variant('i', 41)


def test_get_event_datetime():
    from azafea.event_processors.endless.metrics.utils import get_event_datetime

    assert get_event_datetime(1536122990000000000, 20000000000, 30000000000) \
        == datetime(2018, 9, 5, 4, 50, tzinfo=timezone.utc)
