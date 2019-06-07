import pytest

import chuleisi.utils


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
