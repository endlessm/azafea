# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# Azafea is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Azafea is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Azafea.  If not, see <http://www.gnu.org/licenses/>.


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
