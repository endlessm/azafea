# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from typing import Any


def is_boolean(value: Any) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f'{value!r} is not a boolean')

    return value


def is_non_empty_string(value: Any) -> str:
    if not isinstance(value, str):
        raise TypeError(f'{value!r} is not a string')

    if not value:
        raise ValueError(f'{value!r} is empty')

    return value


def is_strictly_positive_integer(value: Any) -> int:
    if type(value) is not int:
        raise TypeError(f'{value!r} is not an integer')

    if value < 1:
        raise ValueError(f'{value!r} is not a strictly positive integer')

    return value
