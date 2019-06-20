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


import pytest

import azafea.utils


# A dummy process function to use in tests
def process(*args, **kwargs):
    pass


def test_get_cpu_count_failed(monkeypatch):
    def mock_cpu_count():
        # Pretend Python could not find how many CPUs the machine has
        return None

    with monkeypatch.context() as m:
        m.setattr(azafea.utils.os, 'cpu_count', mock_cpu_count)
        assert azafea.utils.get_cpu_count() == 1


@pytest.mark.parametrize('module, name, expected', [
    pytest.param('azafea.logging', 'setup_logging', 'azafea.logging.setup_logging',
                 id='azafea.logging.setup_logging'),
    pytest.param('azafea.controller', 'Controller', 'azafea.controller.Controller',
                 id='azafea.controller.Controller'),
])
def test_get_fqdn(module, name, expected):
    from importlib import import_module

    module = import_module(module)
    f = getattr(module, name)
    assert azafea.utils.get_fqdn(f) == expected


def test_get_handler():
    handler = azafea.utils.get_handler('azafea.tests.test_utils')

    assert handler == process


def test_get_nonexistent_handler_module():
    with pytest.raises(ImportError):
        azafea.utils.get_handler('no.such.module')


def test_get_invalid_handler_module():
    with pytest.raises(AttributeError):
        azafea.utils.get_handler('azafea')


def test_wrap_with_repr(capfd):
    def some_function(some, arguments):
        """An excellent doc string"""
        print(f'Calling some_function({some!r}, {arguments!r})')

    assert repr(some_function) != 'Some super repr'

    wrapped = azafea.utils.wrap_with_repr(some_function, 'Some super repr')
    assert repr(wrapped) == 'Some super repr'
    assert wrapped.__doc__ == 'An excellent doc string'
    assert wrapped.__module__ == 'azafea.tests.test_utils'
    assert wrapped.__name__ == 'some_function'

    wrapped('foo', 42)

    capture = capfd.readouterr()
    assert "Calling some_function('foo', 42)" in capture.out
