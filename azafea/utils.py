# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from importlib import import_module
import os
import sys
from typing import Callable


# The Python documentation for os.cpu_count() says:
#
#     Return the number of CPUs in the system. Returns None if undetermined.
#
# This makes sure to always return an integer.
def get_cpu_count() -> int:
    return os.cpu_count() or 1


def get_fqdn(f: Callable) -> str:
    return f'{f.__module__}.{f.__name__}'


def get_callable(module_name: str, callable_name: str) -> Callable:
    module = import_module(module_name)

    return getattr(module, callable_name)


def progress(current: int, total: int, end: str = '') -> None:
    bar_length = 60

    if not end.endswith('\n') and not sys.stdout.isatty():
        end += '\n'

    if current > total:
        current = total

    if total == 0:
        done = bar_length

    else:
        done = bar_length * current // total

    remaining = bar_length - done

    print(f'\r|{"#" * done}{" " * remaining}|  {current} / {total}', end=end, flush=True)
