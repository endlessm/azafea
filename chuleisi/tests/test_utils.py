import chuleisi.utils


def test_get_cpu_count_failed(monkeypatch):
    def mock_cpu_count():
        # Pretend Python could not find how many CPUs the machine has
        return None

    with monkeypatch.context() as m:
        m.setattr(chuleisi.utils.os, 'cpu_count', mock_cpu_count)
        assert chuleisi.utils.get_cpu_count() == 1
