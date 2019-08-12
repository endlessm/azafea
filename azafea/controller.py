# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


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

    def _exit_cleanly(self) -> None:
        for proc in self._processors:
            proc.join()

        log.info('All workers finished, exiting')
        sys.exit(0)

    def _handle_exit_signals(self, signum: int, _: Any) -> None:
        signal_name = Signals(signum).name
        log.info('Received %s, waiting for workers to finish…', signal_name)

        if signum == SIGTERM:
            # SIGTERM is not automatically sent to subprocesses
            for proc in self._processors:
                proc.terminate()

        self._exit_cleanly()

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
            active_processors = [p for p in self._processors if p.is_alive()]

            if not active_processors:
                self._exit_cleanly()

            time.sleep(1)
