# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


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
