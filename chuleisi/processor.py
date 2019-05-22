import logging
from multiprocessing import Process


log = logging.getLogger(__name__)


class Processor(Process):
    def __init__(self, name: str) -> None:
        super().__init__(name=name)

    def run(self) -> None:
        log.info('{%s} Starting', self.name)
