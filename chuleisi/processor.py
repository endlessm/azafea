import logging
from multiprocessing import Process
from random import randint
from signal import SIGINT, SIGTERM, Signals, signal as intercept_signal
import time
from typing import Any


from .config import Config


log = logging.getLogger(__name__)


class Processor(Process):
    def __init__(self, name: str, config: Config) -> None:
        super().__init__(name=name)

        self.config = config
        self._continue = True

    def _exit_cleanly(self, signum: int, _: Any) -> None:
        signal_name = Signals(signum).name
        log.info('{%s} Received %s, finishing the current task…', self.name, signal_name)
        self._continue = False

    def run(self) -> None:
        log.info('{%s} Starting', self.name)

        intercept_signal(SIGINT, self._exit_cleanly)
        intercept_signal(SIGTERM, self._exit_cleanly)

        while self._continue:
            log.debug('{%s} I am doing some work!', self.name)
            time.sleep(randint(0, 2))
