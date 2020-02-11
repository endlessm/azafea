# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from datetime import datetime, timezone
from threading import RLock
from typing import Any, Dict, Generator, List

from gi.repository import GLib


# This was copy-pasted from the cpython master source code, and can thus be used under the same
# license as Python itself.
#
# We copy the code here because it was only introduced in Python 3.8 which isn't released yet.
#
# All of it can be removed if we move to Python 3.8 as the minimum required version.
_NOT_FOUND = object()


class cached_property:  # pragma: no cover
    def __init__(self, func):  # type: ignore
        self.func = func
        self.attrname = None
        self.__doc__ = func.__doc__
        self.lock = RLock()

    def __set_name__(self, owner, name):  # type: ignore
        if self.attrname is None:
            self.attrname = name
        elif name != self.attrname:
            raise TypeError(
                "Cannot assign the same cached_property to two different names "
                f"({self.attrname!r} and {name!r})."
            )

    def __get__(self, instance, owner):  # type: ignore
        if instance is None:
            return self
        if self.attrname is None:
            raise TypeError(
                "Cannot use cached_property instance without calling __set_name__ on it.")
        try:
            cache = instance.__dict__
        except AttributeError:  # not all objects have __dict__ (e.g. class defines slots)
            msg = (
                f"No '__dict__' attribute on {type(instance).__name__!r} "
                f"instance to cache {self.attrname!r} property."
            )
            raise TypeError(msg) from None
        val = cache.get(self.attrname, _NOT_FOUND)
        if val is _NOT_FOUND:
            with self.lock:
                # check if another thread filled cache while we awaited lock
                val = cache.get(self.attrname, _NOT_FOUND)
                if val is _NOT_FOUND:
                    val = self.func(instance)
                    try:
                        cache[self.attrname] = val
                    except TypeError:
                        msg = (
                            f"The '__dict__' attribute on {type(instance).__name__!r} instance "
                            f"does not support item assignment for caching {self.attrname!r} "
                            "property."
                        )
                        raise TypeError(msg) from None
        return val
# End of the copy-pasted code


# This assumes value is a `ay` variant, verify before calling this
def get_bytes(value: GLib.Variant) -> bytes:
    return bytes(v.get_byte() for v in get_child_values(value))


# This assumes value is an array/tuple variant, verify before calling this
def get_child_values(value: GLib.Variant) -> Generator[GLib.Variant, None, None]:
    return (value.get_child_value(i) for i in range(value.n_children()))


# This assumes value is an `as` or `av<s>` variant, verify before calling this
def get_strings(value: GLib.Variant) -> List[str]:
    return [get_variant(v).get_string() for v in get_child_values(value)]


def get_variant(value: GLib.Variant) -> GLib.Variant:
    # Some of the metric events (e.g UptimeEvent) have payload wrapped multiple times in variants,
    # but others don't
    while value.get_type_string() == 'v':
        value = value.get_variant()

    return value


_VARIANT_GETTERS = {
    'b': lambda v: v.get_boolean(),
    'd': lambda v: v.get_double(),
    'i': lambda v: v.get_int32(),
    'n': lambda v: v.get_int16(),
    'q': lambda v: v.get_uint16(),
    's': lambda v: v.get_string(),
    't': lambda v: v.get_uint64(),
    'u': lambda v: v.get_uint32(),
    'x': lambda v: v.get_int64(),
    'as': get_strings,
}


# This assumes value is an `a{sv}` variant, verify before calling this
def get_asv_dict(value: GLib.Variant) -> Dict[str, Any]:
    result = {}

    for i in range(value.n_children()):
        item = value.get_child_value(i)
        k = item.get_child_value(0).get_string()
        v = get_variant(item.get_child_value(1))
        type_string = v.get_type_string()

        try:
            getter = _VARIANT_GETTERS[type_string]

        except KeyError:
            raise NotImplementedError(f"Can't unpack {type_string!r} variant in {value}")

        result[k] = getter(v)

    return result


# See the timestamp-algorithm.rst file in this directory for details
def get_event_datetime(request_absolute_timestamp: int, request_relative_timestamp: int,
                       event_relative_timestamp: int) -> datetime:
    origin_boot_absolute_timestamp = request_absolute_timestamp - request_relative_timestamp
    event_absolute_timestamp = origin_boot_absolute_timestamp + event_relative_timestamp

    # The timestamps we receive are in nanoseconds
    event_absolute_timestamp_sec = event_absolute_timestamp / 1000000000

    return datetime.fromtimestamp(event_absolute_timestamp_sec, tz=timezone.utc)
