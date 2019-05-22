from chuleisi.logging import setup_logging
import chuleisi.processor


def test_start(capfd):
    setup_logging(verbose=False)

    proc = chuleisi.processor.Processor('test-worker')

    proc.start()
    proc.join()

    capture = capfd.readouterr()
    assert '{test-worker} Starting' in capture.out
