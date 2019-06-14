import logging
from multiprocessing import Process
from signal import SIGINT, SIGTERM, Signals, signal as intercept_signal
from typing import Any

from redis import Redis

from .config import Config
from .model import Db
from .utils import get_fqdn


log = logging.getLogger(__name__)


class Processor(Process):
    def __init__(self, name: str, config: Config) -> None:
        super().__init__(name=name)

        self.config = config
        self._continue = True

        self._redis = Redis(host=config.redis.host, port=config.redis.port)
        self._db = Db(config.postgresql.host, config.postgresql.port, config.postgresql.user,
                      config.postgresql.password, config.postgresql.database)

    def _exit_cleanly(self, signum: int, _: Any) -> None:
        signal_name = Signals(signum).name
        log.info('{%s} Received %s, finishing the current task…', self.name, signal_name)
        self._continue = False

    def run(self) -> None:
        log.info('{%s} Starting', self.name)

        intercept_signal(SIGINT, self._exit_cleanly)
        intercept_signal(SIGTERM, self._exit_cleanly)

        queues = tuple(self.config.queues.keys())
        log.debug('{%s} Pulling from event queues: %s', self.name, queues)

        while self._continue:
            result = self._redis.brpop(queues, timeout=5)

            if result is None:
                continue

            queue, value = result
            queue = queue.decode('utf-8')

            log.debug('{%s} Pulled %s from the %s queue', self.name, value, queue)

            queue_handler = self.config.queues[queue].handler
            log.debug('{%s} Processing event from the %s queue with %s',
                      self.name, queue, get_fqdn(queue_handler))

            try:
                with self._db as dbsession:
                    queue_handler(dbsession, value)

            except Exception:
                log.exception('{%s} An error occured while processing an event from the %s queue '
                              'with %s\nDetails:',
                              self.name, queue, get_fqdn(queue_handler))
                self._redis.lpush(f'errors-{queue}', value)
