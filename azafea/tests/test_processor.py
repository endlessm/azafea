# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import os
import time
from itertools import cycle
from signal import SIGINT, SIGTERM
from typing import Optional

from redis.exceptions import ConnectionError as RedisConnectionError

import pytest

from azafea.config import Config
from azafea.logging import setup_logging
from azafea.model import PostgresqlConnectionError
import azafea.processor


class MockRedis:
    def __init__(self, host: str, port: int, password: str):
        print('Created Redis client')

        self.connection_pool = MockRedisConnectionPool()
        self._values = cycle((b'value', None))

    def rpop(self, key: str, timeout: int = 0) -> Optional[bytes]:
        print(f'Ran Redis command: RPOP {key}')

        return next(self._values)

    def lpush(self, name, *values):
        str_values = b' '.join(values).decode('utf-8')
        print(f'Ran Redis command: LPUSH {name} {str_values}')

        return 1


class MockRedisConnectionPool:
    def make_connection(self):
        return MockRedisConnection()


class MockRedisConnection:
    def connect(self):
        pass


def test_start(capfd, monkeypatch, mock_sessionmaker):
    config = Config()
    setup_logging(verbose=config.main.verbose)

    with monkeypatch.context() as m:
        m.setattr(azafea.processor, 'Redis', MockRedis)
        m.setattr(azafea.model, 'sessionmaker', mock_sessionmaker)
        proc = azafea.processor.Processor('test-worker', config)

    # Prevent the processor from running its main loop
    proc._continue = False

    proc.start()
    proc.join()

    capture = capfd.readouterr()
    assert '{test-worker} Starting' in capture.out


def test_start_then_sigint(capfd, monkeypatch, make_config, mock_sessionmaker):
    def process(*args, **kwargs):
        pass

    def mock_get_callable(module_name, callable_name):
        return process

    with monkeypatch.context() as m:
        m.setattr(azafea.config, 'get_callable', mock_get_callable)
        config = make_config({
            'main': {'verbose': True},
            'queues': {'some-queue': {'handler': 'azafea.tests.test_processor'}},
        })

    setup_logging(verbose=config.main.verbose)

    with monkeypatch.context() as m:
        m.setattr(azafea.processor, 'Redis', MockRedis)
        m.setattr(azafea.model, 'sessionmaker', mock_sessionmaker)
        proc = azafea.processor.Processor('test-worker', config)
        proc.start()

    # Give the process a bit of time to start before sending the signal; 1s should be way enough
    # to pass at least once in the main loop
    time.sleep(1)
    os.kill(proc.pid, SIGINT)

    proc.join()

    capture = capfd.readouterr()
    assert '{test-worker} Starting' in capture.out
    assert "{test-worker} Pulled b'value' from the some-queue queue" in capture.out
    assert '{test-worker} Received SIGINT, finishing the current task…' in capture.out


def test_start_then_sigterm(capfd, monkeypatch, make_config, mock_sessionmaker):
    def process(*args, **kwargs):
        pass

    def mock_get_callable(module_name, callable_name):
        return process

    with monkeypatch.context() as m:
        m.setattr(azafea.config, 'get_callable', mock_get_callable)
        config = make_config({
            'main': {'verbose': True},
            'queues': {'some-queue': {'handler': 'azafea.tests.test_processor'}},
        })

    setup_logging(verbose=config.main.verbose)

    with monkeypatch.context() as m:
        m.setattr(azafea.processor, 'Redis', MockRedis)
        m.setattr(azafea.model, 'sessionmaker', mock_sessionmaker)
        proc = azafea.processor.Processor('test-worker', config)
        proc.start()

    # Give the process a bit of time to start before sending the signal; 1s should be way enough
    # to pass at least once in the main loop
    time.sleep(1)
    os.kill(proc.pid, SIGTERM)

    proc.join()

    capture = capfd.readouterr()
    assert '{test-worker} Starting' in capture.out
    assert "{test-worker} Pulled b'value' from the some-queue queue" in capture.out
    assert '{test-worker} Received SIGTERM, finishing the current task…' in capture.out


def test_process_with_error(capfd, monkeypatch, make_config, mock_sessionmaker):
    def failing_process(*args, **kwargs):
        raise ValueError('Oh no!')

    def mock_get_callable(module_name, callable_name):
        return failing_process

    with monkeypatch.context() as m:
        m.setattr(azafea.config, 'get_callable', mock_get_callable)
        config = make_config({
            'main': {'verbose': True},
            'queues': {'some-queue': {'handler': 'azafea.tests.test_processor'}},
        })

    setup_logging(verbose=config.main.verbose)

    with monkeypatch.context() as m:
        m.setattr(azafea.model, 'sessionmaker', mock_sessionmaker)
        m.setattr(azafea.processor, 'Redis', MockRedis)
        proc = azafea.processor.Processor('test-worker', config)
        proc.start()

    # Give the process a bit of time to start before sending the signal; 1s should be way enough
    # to pass at least once in the main loop
    time.sleep(1)
    os.kill(proc.pid, SIGTERM)

    proc.join()

    capture = capfd.readouterr()
    assert '{test-worker} Starting' in capture.out
    print(capture.out)
    assert "{test-worker} Pulled b'value' from the some-queue queue" in capture.out
    assert ('{test-worker} An error occured while processing an event from the some-queue queue '
            'with azafea.tests.test_processor.failing_process\nDetails:') in capture.err
    assert 'ValueError: Oh no!' in capture.err
    assert 'Ran Redis command: LPUSH errors-some-queue value' in capture.out


def test_cannot_connect_to_redis(monkeypatch, make_config):
    # Hopefully nobody will ever run the tests with a Redis server accessible at this host:port
    config = make_config({'redis': {'host': 'no-such-host', 'port': 1}})

    # Do not monkeypatch Redis here, let it try to actually connect so it fails
    with pytest.raises(RedisConnectionError):
        azafea.processor.Processor('test-worker', config)


def test_cannot_connect_to_postgresql(monkeypatch, make_config):
    # Hopefully nobody will ever run the tests with a Postgres server accessible at this host:port
    config = make_config({'postgresql': {'host': 'no-such-host', 'port': 1}})

    # Do not monkeypatch the DB session here, let it try to actually connect so it fails
    with monkeypatch.context() as m:
        m.setattr(azafea.processor, 'Redis', MockRedis)

        with pytest.raises(PostgresqlConnectionError):
            azafea.processor.Processor('test-worker', config)
