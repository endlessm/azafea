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
from signal import SIGINT, SIGTERM, Signals, signal as intercept_signal
import sys
import time
from typing import Any, List

from .config import Config
from .processor import Processor


log = logging.getLogger(__name__)


class Controller:
    def __init__(self, config: Config) -> None:
        self.config = config
        self._processors: List[Processor] = []

        self._number_of_workers = config.main.number_of_workers

        log.debug('Loaded the following configuration:\n%s', config)

        intercept_signal(SIGINT, self._handle_exit_signals)
        intercept_signal(SIGTERM, self._handle_exit_signals)

    def _handle_exit_signals(self, signum: int, _: Any) -> None:
        signal_name = Signals(signum).name
        log.info('Received %s, waiting for workers to finish…', signal_name)

        if signum == SIGTERM:
            # SIGTERM is not automatically sent to subprocesses
            for proc in self._processors:
                proc.terminate()

        for proc in self._processors:
            proc.join()

        log.info('All workers finished, exiting')
        sys.exit(0)

    def start(self) -> None:
        log.info('Starting the controller with %s worker%s',
                 self._number_of_workers, 's' if self._number_of_workers > 1 else '')

        for i in range(1, self._number_of_workers + 1):
            proc = Processor(f'worker-{i}', self.config)
            proc.start()
            self._processors.append(proc)

    def main(self) -> None:
        self.start()

        while True:
            time.sleep(1)
