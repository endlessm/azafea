import os
from signal import SIGINT, SIGTERM
import time

from chuleisi.logging import setup_logging
import chuleisi.processor


def test_start(capfd):
    setup_logging(verbose=False)

    proc = chuleisi.processor.Processor('test-worker')

    # Prevent the processor from running its main loop
    proc._continue = False

    proc.start()
    proc.join()

    capture = capfd.readouterr()
    assert '{test-worker} Starting' in capture.out


def test_start_then_sigint(capfd):
    setup_logging(verbose=True)

    proc = chuleisi.processor.Processor('test-worker')
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


def test_start_then_sigterm(capfd):
    setup_logging(verbose=True)

    proc = chuleisi.processor.Processor('test-worker')
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
