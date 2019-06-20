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


from importlib import import_module
import os
from typing import Any, Callable, TypeVar


# The Python documentation for os.cpu_count() says:
#
#     Return the number of CPUs in the system. Returns None if undetermined.
#
# This makes sure to always return an integer.
def get_cpu_count() -> int:
    return os.cpu_count() or 1


def get_fqdn(f: Callable) -> str:
    return f'{f.__module__}.{f.__name__}'


def get_handler(module: str) -> Callable:
    handler_module = import_module(module)

    return handler_module.process  # type: ignore


def wrap_with_repr(f: Callable, repr_: str) -> Callable:
    WrappedReturnType = TypeVar('WrappedReturnType')

    class wrapper:
        def __init__(self, to_wrap: Callable[..., WrappedReturnType]):
            self.wrapped = to_wrap
            self.repr = repr_

            self.__doc__ = self.wrapped.__doc__
            self.__module__ = self.wrapped.__module__
            self.__name__ = self.wrapped.__name__

        def __repr__(self) -> str:
            return self.repr

        def __call__(self, *args: Any, **kwargs: Any) -> WrappedReturnType:
            return self.wrapped(*args, **kwargs)

    return wrapper(f)
