import pytest

import chuleisi.utils


# A dummy process function to use in tests
def process(*args, **kwargs):
    pass


def test_get_cpu_count_failed(monkeypatch):
    def mock_cpu_count():
        # Pretend Python could not find how many CPUs the machine has
        return None

    with monkeypatch.context() as m:
        m.setattr(chuleisi.utils.os, 'cpu_count', mock_cpu_count)
        assert chuleisi.utils.get_cpu_count() == 1


@pytest.mark.parametrize('module, name, expected', [
    pytest.param('chuleisi.logging', 'setup_logging', 'chuleisi.logging.setup_logging',
                 id='chuleisi.logging.setup_logging'),
    pytest.param('chuleisi.controller', 'Controller', 'chuleisi.controller.Controller',
                 id='chuleisi.controller.Controller'),
])
def test_get_fqdn(module, name, expected):
    from importlib import import_module

    module = import_module(module)
    f = getattr(module, name)
    assert chuleisi.utils.get_fqdn(f) == expected


def test_get_handler():
    handler = chuleisi.utils.get_handler('chuleisi.tests.test_utils')

    assert handler == process


def test_get_nonexistent_handler_module():
    with pytest.raises(ImportError):
        chuleisi.utils.get_handler('no.such.module')


def test_get_invalid_handler_module():
    with pytest.raises(AttributeError):
        chuleisi.utils.get_handler('chuleisi')


def test_wrap_with_repr(capfd):
    def some_function(some, arguments):
        """An excellent doc string"""
        print(f'Calling some_function({some!r}, {arguments!r})')

    assert repr(some_function) != 'Some super repr'

    wrapped = chuleisi.utils.wrap_with_repr(some_function, 'Some super repr')
    assert repr(wrapped) == 'Some super repr'
    assert wrapped.__doc__ == 'An excellent doc string'
    assert wrapped.__module__ == 'chuleisi.tests.test_utils'
    assert wrapped.__name__ == 'some_function'

    wrapped('foo', 42)

    capture = capfd.readouterr()
    assert "Calling some_function('foo', 42)" in capture.out
