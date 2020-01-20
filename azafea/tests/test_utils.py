# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


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


def test_get_callable():
    handler = azafea.utils.get_callable('azafea.tests.test_utils', 'process')

    assert handler == process


def test_get_nonexistent_callable_module():
    with pytest.raises(ImportError):
        azafea.utils.get_callable('no.such.module', 'process')


def test_get_invalid_callable_module():
    with pytest.raises(AttributeError):
        azafea.utils.get_callable('azafea.tests.test_utils', 'no_such_method')


def test_progress(capfd):
    azafea.utils.progress(0, 6)

    capture = capfd.readouterr()
    assert capture.out == (
        '\r|                                                            |  0 / 6\n')

    azafea.utils.progress(2, 6)

    capture = capfd.readouterr()
    assert capture.out == (
        '\r|####################                                        |  2 / 6\n')

    azafea.utils.progress(4, 6)

    capture = capfd.readouterr()
    assert capture.out == (
        '\r|########################################                    |  4 / 6\n')

    azafea.utils.progress(6, 6, end='\n')

    capture = capfd.readouterr()
    assert capture.out == (
        '\r|############################################################|  6 / 6\n')


def test_progress_zero(capfd):
    azafea.utils.progress(0, 0, end='\n')

    capture = capfd.readouterr()
    assert capture.out == (
        '\r|############################################################|  0 / 0\n')


def test_progress_over(capfd):
    azafea.utils.progress(8, 6, end='\n')

    capture = capfd.readouterr()
    assert capture.out == (
        '\r|############################################################|  6 / 6\n')
