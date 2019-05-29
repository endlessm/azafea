import os
from signal import SIGINT, SIGTERM
import time

from chuleisi.config import Config
from chuleisi.logging import setup_logging
import chuleisi.processor


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


def test_start_then_sigint(capfd, make_config):
    config = make_config({'main': {'verbose': True}})
    setup_logging(verbose=config.main.verbose)

    proc = chuleisi.processor.Processor('test-worker', config)
    proc.start()

    # Give the process a bit of time to start before sending the signal; 0.1s should be way enough
    # to pass at least once in the main loop
    time.sleep(0.1)
    os.kill(proc.pid, SIGINT)

    proc.join()

    capture = capfd.readouterr()
    assert '{test-worker} Starting' in capture.out
    assert '{test-worker} I am doing some work!' in capture.out
    assert '{test-worker} Received SIGINT, finishing the current task…' in capture.out


def test_start_then_sigterm(capfd, make_config):
    config = make_config({'main': {'verbose': True}})
    setup_logging(verbose=config.main.verbose)

    proc = chuleisi.processor.Processor('test-worker', config)
    proc.start()

    # Give the process a bit of time to start before sending the signal; 0.1s should be way enough
    # to pass at least once in the main loop
    time.sleep(0.1)
    os.kill(proc.pid, SIGTERM)

    proc.join()

    capture = capfd.readouterr()
    assert '{test-worker} Starting' in capture.out
    assert '{test-worker} I am doing some work!' in capture.out
    assert '{test-worker} Received SIGTERM, finishing the current task…' in capture.out
