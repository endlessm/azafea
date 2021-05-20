# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import logging
from datetime import datetime, timezone
from typing import Generator

from gi.repository import GLib


log = logging.getLogger(__name__)


# This assumes value is a `ay` variant, verify before calling this
def get_bytes(value: GLib.Variant) -> bytes:
    return bytes(v.get_byte() for v in get_child_values(value))


# This assumes value is an array/tuple variant, verify before calling this
def get_child_values(value: GLib.Variant) -> Generator[GLib.Variant, None, None]:
    return (value.get_child_value(i) for i in range(value.n_children()))


def get_variant(value: GLib.Variant) -> GLib.Variant:
    # Some of the metric events (e.g UptimeEvent) have payload wrapped multiple times in variants,
    # but others don't
    while value.get_type_string() == 'v':
        value = value.get_variant()

    return value


# See the timestamp-algorithm.rst file in this directory for details
def get_event_datetime(request_absolute_timestamp: int, request_relative_timestamp: int,
                       event_relative_timestamp: int) -> datetime:
    origin_boot_absolute_timestamp = request_absolute_timestamp - request_relative_timestamp
    event_absolute_timestamp = origin_boot_absolute_timestamp + event_relative_timestamp

    # The timestamps we receive are in nanoseconds
    event_absolute_timestamp_sec = event_absolute_timestamp / 1000000000

    return datetime.fromtimestamp(event_absolute_timestamp_sec, tz=timezone.utc)


def clamp_to_int64(u64: int) -> int:
    if u64 > GLib.MAXINT64:
        log.error(f'Clamped integer larger than MAXINT64: {u64}')
        return GLib.MAXINT64
    else:
        return u64
