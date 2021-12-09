# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from datetime import datetime, timezone
from gi.repository import GLib
import logging

import pytest


def test_get_bytes():
    from azafea.event_processors.endless.metrics.v2.utils import get_bytes

    variant = GLib.Variant('ay', b'some bytes')
    assert get_bytes(variant) == b'some bytes'


def test_get_child_values():
    from azafea.event_processors.endless.metrics.v2.utils import get_child_values

    variant = GLib.Variant('ay', b'123')
    assert list(get_child_values(variant)) == [
        GLib.Variant('y', b'1'),
        GLib.Variant('y', b'2'),
        GLib.Variant('y', b'3'),
    ]


@pytest.mark.parametrize('variant', [
    GLib.Variant('v', GLib.Variant('i', 41)),
    GLib.Variant('v', GLib.Variant('v', GLib.Variant('i', 41))),
    GLib.Variant('v', GLib.Variant('v', GLib.Variant('v', GLib.Variant('i', 41)))),
])
def test_get_variant(variant):
    from azafea.event_processors.endless.metrics.v2.utils import get_variant

    assert get_variant(variant) == GLib.Variant('i', 41)


def test_get_event_datetime():
    from azafea.event_processors.endless.metrics.v2.utils import get_event_datetime

    assert get_event_datetime(1536122990000000000, 20000000000, 30000000000) \
        == datetime(2018, 9, 5, 4, 50, tzinfo=timezone.utc)


def test_clamp_to_int64(caplog):
    from azafea.event_processors.endless.metrics.v2.utils import clamp_to_int64, log as utils_log

    val = clamp_to_int64(GLib.MAXUINT64)
    assert val == GLib.MAXINT64
    assert caplog.records != []

    # Check that the message and exception come through.
    record = caplog.records[0]
    assert record.name == utils_log.name
    assert record.levelno == logging.ERROR
    assert record.msg == f'Clamped integer larger than MAXINT64: {GLib.MAXUINT64}'
    assert record.exc_info is not None
    assert record.exc_info[0] == ValueError
    assert str(record.exc_info[1]) == f'{GLib.MAXUINT64} larger than {GLib.MAXINT64}'

    caplog.clear()
    val = clamp_to_int64(GLib.MAXINT64)
    assert val == GLib.MAXINT64
    assert caplog.records == []

    caplog.clear()
    val = clamp_to_int64(GLib.MAXINT64 + 1)
    assert val == GLib.MAXINT64
    assert caplog.records != []
