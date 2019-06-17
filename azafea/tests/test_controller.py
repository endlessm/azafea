from signal import SIGINT, SIGTERM

import pytest

from azafea.config import Config
import azafea.controller
from azafea.logging import setup_logging
from azafea.utils import get_cpu_count


class MockProcessor:
    def __init__(self, name, config):
        self.name = name
        self.joined = False
        self.terminated = False

    def start(self):
        print('{%s} Starting' % self.name)

    def join(self):
        self.joined = True

    def terminate(self):
        self.terminated = True


def test_start(capfd, monkeypatch):
    config = Config()
    setup_logging(verbose=config.main.verbose)

    with monkeypatch.context() as m:
        m.setattr(azafea.controller, 'Processor', MockProcessor)
        controller = azafea.controller.Controller(config)
        controller.start()

    number = get_cpu_count()
    assert len(controller._processors) == number

    capture = capfd.readouterr()
    assert f'Starting the controller with {number} workers' in capture.out

    for i in range(1, number + 1):
        assert f'{{worker-{i}}} Starting' in capture.out


def test_override_num_workers(capfd, monkeypatch, make_config):
    config = make_config({'main': {'number_of_workers': 1}})
    setup_logging(verbose=config.main.verbose)

    with monkeypatch.context() as m:
        m.setattr(azafea.controller, 'Processor', MockProcessor)
        controller = azafea.controller.Controller(config)
        controller.start()

    number = get_cpu_count()
    assert len(controller._processors) == 1

    capture = capfd.readouterr()
    assert 'Starting the controller with 1 worker' in capture.out
    assert '{worker-1} Starting' in capture.out

    if number > 1:
        assert f'{{worker-{number}}} Starting' not in capture.out


def test_sigint_handler(capfd, make_config):
    config = make_config({'main': {'number_of_workers': 1}})
    setup_logging(verbose=config.main.verbose)

    with pytest.raises(SystemExit) as exc_info:
        controller = azafea.controller.Controller(config)
        controller._processors = [MockProcessor('test-worker', config)]
        controller._exit_cleanly(SIGINT, None)

    for proc in controller._processors:
        assert proc.joined
        assert not proc.terminated

    capture = capfd.readouterr()
    assert 'Received SIGINT, waiting for workers to finish…' in capture.out
    assert 'All workers finished, exiting' in capture.out

    assert exc_info.value.args == (0, )


def test_sigterm_handler(capfd, make_config):
    config = make_config({'main': {'number_of_workers': 1}})
    setup_logging(verbose=config.main.verbose)

    with pytest.raises(SystemExit) as exc_info:
        controller = azafea.controller.Controller(config)
        controller._processors = [MockProcessor('test-worker', config)]
        controller._exit_cleanly(SIGTERM, None)

    for proc in controller._processors:
        assert proc.joined
        assert proc.terminated

    capture = capfd.readouterr()
    assert 'Received SIGTERM, waiting for workers to finish…' in capture.out
    assert 'All workers finished, exiting' in capture.out

    assert exc_info.value.args == (0, )
