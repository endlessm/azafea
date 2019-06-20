# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# Azafea is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Azafea is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Azafea.  If not, see <http://www.gnu.org/licenses/>.


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
