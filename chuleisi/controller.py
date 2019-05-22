import logging
from typing import List

from .logging import setup_logging
from .processor import Processor
from .utils import get_cpu_count


log = logging.getLogger(__name__)


class Controller:
    def __init__(self) -> None:
        self._processors: List[Processor] = []

        # TODO: Get this from a configuration file
        setup_logging(verbose=True)

        # TODO: Get this from a configuration file
        self._number_of_workers = get_cpu_count()

    def start(self) -> None:
        log.info('Starting the controller with %s worker%s',
                 self._number_of_workers, 's' if self._number_of_workers > 1 else '')

        for i in range(1, self._number_of_workers + 1):
            proc = Processor(f'worker-{i}')
            proc.start()
            self._processors.append(proc)

    def main(self) -> None:
        self.start()

        for proc in self._processors:
            proc.join()

        log.info('All workers finished, exiting')
