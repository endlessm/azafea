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
    with monkeypatch.context() as m:
        m.setattr(chuleisi.controller, 'Processor', MockProcessor)
        controller = chuleisi.controller.Controller()
        controller.start()

    number = get_cpu_count()
    assert len(controller._processors) == number

    capture = capfd.readouterr()
    assert f'Starting the controller with {number} workers' in capture.out

    for i in range(1, number + 1):
        assert f'{{worker-{i}}} Starting' in capture.out
