# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


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

        self._redis = self._get_redis()
        self._db = self._get_postgresql()

    def _exit_cleanly(self, signum: int, _: Any) -> None:
        signal_name = Signals(signum).name
        log.info('{%s} Received %s, finishing the current task…', self.name, signal_name)
        self._continue = False

    def _get_postgresql(self) -> Db:
        return Db(self.config.postgresql)

    def _get_redis(self) -> Redis:
        redis = Redis(host=self.config.redis.host, port=self.config.redis.port,
                      password=self.config.redis.password)

        # Try to connect, to fail early if the Redis server can't be reached. The connection
        # disconnects automatically when garbage collected.
        redis.connection_pool.make_connection().connect()

        return redis

    def run(self) -> None:
        log.info('{%s} Starting', self.name)

        intercept_signal(SIGINT, self._exit_cleanly)
        intercept_signal(SIGTERM, self._exit_cleanly)

        queues = tuple(self.config.queues.keys())
        log.debug('{%s} Pulling from event queues: %s', self.name, queues)

        while self._continue:
            if self.config.main.exit_on_empty_queues:
                for queue in queues:
                    value = self._redis.rpop(queue)
                    if value:
                        break
            else:
                result = self._redis.brpop(queues, timeout=5)
                if result is None:
                    value = None
                else:
                    queue_bytes, value = result
                    queue = queue_bytes.decode('utf-8')

            if value is None:
                if self.config.main.exit_on_empty_queues:
                    log.info('{%s} Event queues are empty, exiting', self.name)
                    break

                log.debug('{%s} Pulled nothing from the queues and timed out', self.name)
                continue

            log.debug('{%s} Pulled %s from the %s queue', self.name, value, queue)

            queue_processor = self.config.queues[queue].processor
            log.debug('{%s} Processing event from the %s queue with %s',
                      self.name, queue, get_fqdn(queue_processor))

            try:
                with self._db as dbsession:
                    queue_processor(dbsession, value)

            except Exception:
                log.exception('{%s} An error occured while processing an event from the %s queue '
                              'with %s\nDetails:',
                              self.name, queue, get_fqdn(queue_processor))
                self._redis.lpush(f'errors-{queue}', value)
