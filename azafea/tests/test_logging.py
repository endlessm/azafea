import logging

from azafea.logging import setup_logging


def test_default(capfd):
    setup_logging(verbose=False)
    log = logging.getLogger(__name__)

    log.debug('A debugging message')
    log.info('An informative message')
    log.warning('A scary warning')
    log.error('Oh no!')

    capture = capfd.readouterr()
    assert 'A debugging message' not in capture.out
    assert 'An informative message' in capture.out
    assert 'A scary warning' in capture.err
    assert 'Oh no!' in capture.err


def test_verbose(capfd):
    setup_logging(verbose=True)
    log = logging.getLogger(__name__)

    log.debug('A debugging message')
    log.info('An informative message')
    log.warning('A scary warning')
    log.error('Oh no!')

    capture = capfd.readouterr()
    assert 'A debugging message' in capture.out
    assert 'An informative message' in capture.out
    assert 'A scary warning' in capture.err
    assert 'Oh no!' in capture.err


def test_reset_logging(capfd):
    setup_logging(verbose=False)
    log = logging.getLogger(__name__)

    log.debug('A debugging message')
    capture = capfd.readouterr()
    assert 'A debugging message' not in capture.out

    setup_logging(verbose=True)

    log.debug('A debugging message')
    capture = capfd.readouterr()
    assert 'A debugging message' in capture.out

    setup_logging(verbose=False)

    log.debug('A debugging message')
    capture = capfd.readouterr()
    assert 'A debugging message' not in capture.out
