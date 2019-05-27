import os
from signal import SIGINT, SIGTERM
import time
from typing import Optional, Sequence, Tuple

from chuleisi.config import Config
from chuleisi.logging import setup_logging
import chuleisi.processor


class MockRedis:
    def __init__(self, host: str, port: int):
        print('Created Redis client')

        # FIXME: This is a hack just to have code coverage of the cases BRPOP returns None (the
        # timeout was reached) as well as when it returns a value. Figure out a way to test this
        # properly.
        self._next_key = 0
        self._next_value = 0

    def brpop(self, keys: Sequence[str], timeout: int = 0) -> Optional[Tuple[bytes, bytes]]:
        str_keys = ' '.join(keys)
        print(f'Ran Redis command: BRPOP {str_keys}')

        value = (None, b'value')[self._next_value]
        self._next_value = (self._next_value + 1) % 2

        if value is None:
            return None

        # Note: this only works if the number of queues doesn't change after having created the
        # Redis client. In this application the configuration is only loaded at startup so this is
        # a fair assumption.
        key = keys[self._next_key]
        self._next_key = (self._next_key + 1) % len(keys)

        return key.encode('utf-8'), value


def test_start(capfd):
    config = Config()
    setup_logging(verbose=config.main.verbose)

    proc = chuleisi.processor.Processor('test-worker', config)

    # Prevent the processor from running its main loop
    proc._continue = False

    proc.start()
    proc.join()

    capture = capfd.readouterr()
    assert '{test-worker} Starting' in capture.out


def test_start_then_sigint(capfd, monkeypatch, make_config):
    config = make_config({'main': {'verbose': True}})
    setup_logging(verbose=config.main.verbose)

    with monkeypatch.context() as m:
        m.setattr(chuleisi.processor, 'Redis', MockRedis)
        proc = chuleisi.processor.Processor('test-worker', config)
        proc.start()

    # Give the process a bit of time to start before sending the signal; 0.1s should be way enough
    # to pass at least once in the main loop
    time.sleep(0.1)
    os.kill(proc.pid, SIGINT)

    proc.join()

    capture = capfd.readouterr()
    assert '{test-worker} Starting' in capture.out
    assert '{test-worker} Pulled "value" from the ' in capture.out
    assert '{test-worker} Received SIGINT, finishing the current task…' in capture.out


def test_start_then_sigterm(capfd, monkeypatch, make_config):
    config = make_config({'main': {'verbose': True}})
    setup_logging(verbose=config.main.verbose)

    with monkeypatch.context() as m:
        m.setattr(chuleisi.processor, 'Redis', MockRedis)
        proc = chuleisi.processor.Processor('test-worker', config)
        proc.start()

    # Give the process a bit of time to start before sending the signal; 0.1s should be way enough
    # to pass at least once in the main loop
    time.sleep(0.1)
    os.kill(proc.pid, SIGTERM)

    proc.join()

    capture = capfd.readouterr()
    assert '{test-worker} Starting' in capture.out
    assert '{test-worker} Pulled "value" from the ' in capture.out
    assert '{test-worker} Received SIGTERM, finishing the current task…' in capture.out
