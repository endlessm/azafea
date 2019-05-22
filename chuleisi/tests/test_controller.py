from chuleisi.config import Config
import chuleisi.controller
from chuleisi.utils import get_cpu_count


class MockProcessor:
    def __init__(self, name):
        self.name = name

    def start(self):
        print('{%s} Starting' % self.name)

    def join(self):
        pass


def test_start(capfd, monkeypatch):
    config = Config()

    with monkeypatch.context() as m:
        m.setattr(chuleisi.controller, 'Processor', MockProcessor)
        controller = chuleisi.controller.Controller(config)
        controller.start()

    number = get_cpu_count()
    assert len(controller._processors) == number

    capture = capfd.readouterr()
    assert f'Starting the controller with {number} workers' in capture.out

    for i in range(1, number + 1):
        assert f'{{worker-{i}}} Starting' in capture.out


def test_override_num_workers(capfd, monkeypatch, make_config):
    config = make_config({'main': {'number_of_workers': 1}})

    with monkeypatch.context() as m:
        m.setattr(chuleisi.controller, 'Processor', MockProcessor)
        controller = chuleisi.controller.Controller(config)
        controller.start()

    number = get_cpu_count()
    assert len(controller._processors) == 1

    capture = capfd.readouterr()
    assert 'Starting the controller with 1 worker' in capture.out
    assert '{worker-1} Starting' in capture.out

    if number > 1:
        assert f'{{worker-{number}}} Starting' not in capture.out
