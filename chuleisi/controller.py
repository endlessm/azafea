import logging
from signal import SIGINT, SIGTERM, Signals, signal as intercept_signal
import sys
import time
from typing import Any, List

from .config import Config
from .logging import setup_logging
from .processor import Processor


log = logging.getLogger(__name__)


class Controller:
    def __init__(self, config: Config) -> None:
        self.config = config
        self._processors: List[Processor] = []

        setup_logging(verbose=config.main.verbose)

        self._number_of_workers = config.main.number_of_workers

        log.debug('Loaded the following configuration:\n%s', config)

        intercept_signal(SIGINT, self._exit_cleanly)
        intercept_signal(SIGTERM, self._exit_cleanly)

    def _exit_cleanly(self, signum: int, _: Any) -> None:
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
            proc = Processor(f'worker-{i}')
            proc.start()
            self._processors.append(proc)

    def main(self) -> None:
        self.start()

        while True:
            time.sleep(1)
