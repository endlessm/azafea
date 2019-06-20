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
import sys


class StdoutFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= logging.INFO


def _reset_logging() -> None:
    # This is necessary for 2 reasons:
    #
    # 1.  pytest sets up the logging system (to capture logs) which means when setup_logging is
    #     called its setup is ignored;
    # 2.  after calling setup_logging once, calling a second time doesn't do anything either;
    #
    # Both issues make it impossible to properly test the setup_logging function without resetting
    # the log setup.
    #
    # As this undoes the logging setup pytest does though, it means we can't use their caplog
    # fixture. Instead, log messages are sent to their capsys/capfd fixtures.
    root = logging.getLogger()

    for handler in root.handlers[:]:
        handler.close()
        root.removeHandler(handler)


def setup_logging(*, verbose: bool = False) -> None:
    _reset_logging()

    level = logging.DEBUG if verbose else logging.INFO

    # Send DEBUG and INFO to stdout, WARNING and ERROR to stderr
    out = logging.StreamHandler(stream=sys.stdout)
    out.setLevel(logging.DEBUG)
    out.addFilter(StdoutFilter())
    err = logging.StreamHandler(stream=sys.stderr)
    err.setLevel(logging.WARNING)

    format_ = '[{levelname}] {name}: {message}'
    logging.basicConfig(level=level, handlers=[out, err], format=format_, style='{')

    if verbose:
        # Increase verbosity
        logging.getLogger('sqlalchemy').setLevel(logging.DEBUG)

        # Decrease verbosity
        logging.getLogger('flake8').setLevel(logging.WARNING)
