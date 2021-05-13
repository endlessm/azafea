# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import pytest

import azafea.cli
import azafea.config


def test_dropdb(capfd, monkeypatch, make_config_file):
    class MockDb:
        def __init__(self, *args):
            pass

        def drop_all(self):
            print('Dropping the tables…')

    def mock_get_callable(module_name, callable_name):
        def process(*args, **kwargs):
            pass

        return process

    config_file = make_config_file({'queues': {'some-queue': {'handler': 'azafea.tests.test_cli'}}})

    with monkeypatch.context() as m:
        m.setattr(azafea.config, 'get_callable', mock_get_callable)
        m.setattr(azafea.cli.commands, 'Db', MockDb)
        azafea.cli.run_command('-c', str(config_file), 'dropdb')

    capture = capfd.readouterr()
    assert 'Dropping the tables…' in capture.out


def test_dropdb_invalid_config(capfd, make_config_file):
    # Make a wrong config file
    config_file = make_config_file({'main': {'verbose': 'blah'}})

    with pytest.raises(azafea.cli.errors.InvalidConfigExit):
        azafea.cli.run_command('-c', str(config_file), 'dropdb')

    capture = capfd.readouterr()
    assert "Invalid configuration:\n* main.verbose: 'blah' is not a boolean" in capture.err


def test_dropdb_no_event_queue(capfd, make_config_file):
    config_file = make_config_file({})

    with pytest.raises(azafea.cli.errors.NoEventQueueExit):
        azafea.cli.run_command('-c', str(config_file), 'dropdb')

    capture = capfd.readouterr()
    assert "Could not clear the database: no event queue configured" in capture.err


def test_initdb(capfd, monkeypatch, make_config_file):
    class MockDb:
        def __init__(self, *args):
            pass

        def create_all(self):
            print('Creating the tables…')

    def mock_get_callable(module_name, callable_name):
        def process(*args, **kwargs):
            pass

        return process

    config_file = make_config_file({'queues': {'some-queue': {'handler': 'azafea.tests.test_cli'}}})

    with monkeypatch.context() as m:
        m.setattr(azafea.config, 'get_callable', mock_get_callable)
        m.setattr(azafea.cli.commands, 'Db', MockDb)
        azafea.cli.run_command('-c', str(config_file), 'initdb')

    capture = capfd.readouterr()
    assert 'Creating the tables…' in capture.out


def test_initdb_invalid_config(capfd, make_config_file):
    # Make a wrong config file
    config_file = make_config_file({'main': {'verbose': 'blah'}})

    with pytest.raises(azafea.cli.errors.InvalidConfigExit):
        azafea.cli.run_command('-c', str(config_file), 'initdb')

    capture = capfd.readouterr()
    assert "Invalid configuration:\n* main.verbose: 'blah' is not a boolean" in capture.err


def test_initdb_no_event_queue(capfd, make_config_file):
    config_file = make_config_file({})

    with pytest.raises(azafea.cli.errors.NoEventQueueExit):
        azafea.cli.run_command('-c', str(config_file), 'initdb')

    capture = capfd.readouterr()
    assert "Could not initialize the database: no event queue configured" in capture.err


def test_make_migration_invalid_config(capfd, make_config_file):
    # Make a wrong config file
    config_file = make_config_file({'main': {'verbose': 'blah'}})

    with pytest.raises(azafea.cli.errors.InvalidConfigExit):
        azafea.cli.run_command('-c', str(config_file), 'make-migration', 'some-queue')

    capture = capfd.readouterr()
    assert "Invalid configuration:\n* main.verbose: 'blah' is not a boolean" in capture.err


def test_make_migration_no_event_queue(capfd, make_config_file):
    config_file = make_config_file({})

    with pytest.raises(azafea.cli.errors.NoEventQueueExit):
        azafea.cli.run_command('-c', str(config_file), 'make-migration', 'some-queue')

    capture = capfd.readouterr()
    assert (
        'Could not generate a migration for "some-queue": no event queue configured') in capture.err


def test_make_migration_unknown_queue(capfd, monkeypatch, make_config_file):
    def mock_get_callable(module_name, callable_name):
        def process(*args, **kwargs):
            pass

        return process

    config_file = make_config_file({
        'queues': {'some-queue': {'handler': 'azafea.tests.test_cli'}},
    })

    with monkeypatch.context() as m:
        m.setattr(azafea.config, 'get_callable', mock_get_callable)

        with pytest.raises(azafea.cli.errors.NoEventQueueExit):
            azafea.cli.run_command('-c', str(config_file), 'make-migration', 'other-queue')

    capture = capfd.readouterr()
    assert ('Could not generate a migration for "other-queue": '
            'unknown event queue requested') in capture.err


def test_make_migration_no_migrations(capfd, monkeypatch, make_config_file):
    def mock_get_callable(module_name, callable_name):
        def process(*args, **kwargs):
            pass

        return process

    config_file = make_config_file({
        'queues': {'some-queue': {'handler': 'azafea.tests.test_cli'}},
    })

    with monkeypatch.context() as m:
        m.setattr(azafea.config, 'get_callable', mock_get_callable)

        azafea.cli.run_command('-c', str(config_file), 'make-migration', 'some-queue')

    capture = capfd.readouterr()
    assert "Configured queue handlers don't have 'migrations' directories" in capture.out


def test_migratedb_invalid_config(capfd, make_config_file):
    # Make a wrong config file
    config_file = make_config_file({'main': {'verbose': 'blah'}})

    with pytest.raises(azafea.cli.errors.InvalidConfigExit):
        azafea.cli.run_command('-c', str(config_file), 'migratedb')

    capture = capfd.readouterr()
    assert "Invalid configuration:\n* main.verbose: 'blah' is not a boolean" in capture.err


def test_migratedb_no_event_queue(capfd, make_config_file):
    config_file = make_config_file({})

    with pytest.raises(azafea.cli.errors.NoEventQueueExit):
        azafea.cli.run_command('-c', str(config_file), 'migratedb')

    capture = capfd.readouterr()
    assert 'Could not migrate the database: no event queue configured' in capture.err


def test_migratedb_no_migrations(capfd, monkeypatch, make_config_file):
    def mock_get_callable(module_name, callable_name):
        def process(*args, **kwargs):
            pass

        return process

    config_file = make_config_file({
        'queues': {'some-queue': {'handler': 'azafea.tests.test_cli'}},
    })

    with monkeypatch.context() as m:
        m.setattr(azafea.config, 'get_callable', mock_get_callable)

        azafea.cli.run_command('-c', str(config_file), 'migratedb')

    capture = capfd.readouterr()
    assert "Configured queue handlers don't have migrations" in capture.out


def test_print_config(capfd, monkeypatch, make_config_file):
    def mock_get_callable(module_name, callable_name):
        def process(*args, **kwargs):
            pass

        return process

    config_file = make_config_file({
        'main': {'number_of_workers': 1},
        'redis': {'host': 'redis-server'},
        'postgresql': {'user': 'Léo'},
        'queues': {'some-queue': {'handler': 'azafea.tests.test_cli'}},
    })

    with monkeypatch.context() as m:
        m.setattr(azafea.config, 'get_callable', mock_get_callable)
        azafea.cli.run_command('-c', str(config_file), 'print-config')

    capture = capfd.readouterr()
    assert capture.out.strip() == '\n'.join([
        '----- BEGIN -----',
        '[main]',
        'verbose = false',
        'number_of_workers = 1',
        'exit_on_empty_queues = false',
        '',
        '[redis]',
        'host = "redis-server"',
        'port = 6379',
        'password = "** hidden **"',
        '',
        '[postgresql]',
        'host = "localhost"',
        'port = 5432',
        'user = "Léo"',
        'password = "** hidden **"',
        'database = "azafea"',
        '',
        '[postgresql.connect_args]',
        '',
        '[queues.some-queue]',
        'handler = "azafea.tests.test_cli"',
        '------ END ------',
    ])


def test_print_invalid_config(capfd, make_config_file):
    # Make a wrong config file
    config_file = make_config_file({'main': {'verbose': 'blah'}})

    with pytest.raises(azafea.cli.errors.InvalidConfigExit):
        azafea.cli.run_command('-c', str(config_file), 'print-config')

    capture = capfd.readouterr()
    assert "Invalid configuration:\n* main.verbose: 'blah' is not a boolean" in capture.err


def test_print_config_no_event_queue(capfd, make_config_file):
    config_file = make_config_file({})

    with pytest.raises(azafea.cli.errors.NoEventQueueExit):
        azafea.cli.run_command('-c', str(config_file), 'print-config')

    capture = capfd.readouterr()
    assert "Did you forget to configure event queues?" in capture.err


def test_replay_errors(capfd, monkeypatch, make_config_file):
    class MockRedis:
        def __init__(self):
            self._queues = {
                'some-queue': [],
                'errors-some-queue': [b'event1', b'event2', b'event3'],
            }

        def llen(self, queue_name):
            return len(self._queues[queue_name])

        def lpush(self, queue_name, value):
            self._queues[queue_name].insert(0, value)

        def rpop(self, queue_name):
            try:
                return self._queues[queue_name].pop(-1)

            except IndexError:
                return None

    redis = MockRedis()

    def mock_redis(*args, **kwargs):
        return redis

    def mock_get_callable(module_name, callable_name):
        def process(*args, **kwargs):
            pass

        return process

    config_file = make_config_file({
        'queues': {'some-queue': {'handler': 'azafea.tests.test_cli'}},
    })

    with monkeypatch.context() as m:
        m.setattr(azafea.cli.commands, 'Redis', mock_redis)
        m.setattr(azafea.config, 'get_callable', mock_get_callable)
        azafea.cli.run_command('-c', str(config_file), 'replay-errors', 'some-queue')

    assert redis._queues == {
        'some-queue': [b'event1', b'event2', b'event3'],
        'errors-some-queue': [],
    }

    capture = capfd.readouterr()
    assert 'Successfully moved failed events back to "some-queue"' in capture.out


def test_replay_errors_invalid_config(capfd, make_config_file):
    # Make a wrong config file
    config_file = make_config_file({'main': {'verbose': 'blah'}})

    with pytest.raises(azafea.cli.errors.InvalidConfigExit):
        azafea.cli.run_command('-c', str(config_file), 'replay-errors', 'some-queue')

    capture = capfd.readouterr()
    assert "Invalid configuration:\n* main.verbose: 'blah' is not a boolean" in capture.err


def test_replay_errors_no_event_queue(capfd, make_config_file):
    config_file = make_config_file({})

    with pytest.raises(azafea.cli.errors.NoEventQueueExit):
        azafea.cli.run_command('-c', str(config_file), 'replay-errors', 'some-queue')

    capture = capfd.readouterr()
    assert 'Could not replay events from "some-queue": no event queue configured' in capture.err


def test_replay_errors_unknown_queue(capfd, monkeypatch, make_config_file):
    def mock_get_callable(module_name, callable_name):
        def process(*args, **kwargs):
            pass

        return process

    config_file = make_config_file({
        'queues': {'some-queue': {'handler': 'azafea.tests.test_cli'}},
    })

    with monkeypatch.context() as m:
        m.setattr(azafea.config, 'get_callable', mock_get_callable)

        with pytest.raises(azafea.cli.errors.NoEventQueueExit):
            azafea.cli.run_command('-c', str(config_file), 'replay-errors', 'other-queue')

    capture = capfd.readouterr()
    assert ('Could not replay events from "other-queue": '
            'unknown event queue requested') in capture.err


def test_replay_errors_stopped_early(capfd, monkeypatch, make_config_file):
    class MockRedis:
        def __init__(self):
            self._queues = {
                'some-queue': [],
                'errors-some-queue': [b'event1', b'event2', b'event3'],
            }

        def llen(self, queue_name):
            # Pretend there were 5 elements in the queue but somehow only 3 could be pulled
            return 5

        def lpush(self, queue_name, value):
            self._queues[queue_name].insert(0, value)

        def rpop(self, queue_name):
            try:
                return self._queues[queue_name].pop(-1)

            except IndexError:
                return None

    redis = MockRedis()

    def mock_redis(*args, **kwargs):
        return redis

    def mock_get_callable(module_name, callable_name):
        def process(*args, **kwargs):
            pass

        return process

    config_file = make_config_file({
        'queues': {'some-queue': {'handler': 'azafea.tests.test_cli'}},
    })

    with monkeypatch.context() as m:
        m.setattr(azafea.cli.commands, 'Redis', mock_redis)
        m.setattr(azafea.config, 'get_callable', mock_get_callable)
        azafea.cli.run_command('-c', str(config_file), 'replay-errors', 'some-queue')

    assert redis._queues == {
        'some-queue': [b'event1', b'event2', b'event3'],
        'errors-some-queue': [],
    }

    capture = capfd.readouterr()
    assert '"some-queue" emptied faster than planned after 3 elements out of 5' in capture.err
    assert 'Successfully moved failed events back to "some-queue"' in capture.out


def test_replay_errors_fail_to_push(capfd, monkeypatch, make_config_file):
    class MockRedis:
        def __init__(self):
            self._queues = {
                'some-queue': [],
                'errors-some-queue': [b'event1', b'event2', b'event3'],
            }

        def llen(self, queue_name):
            return len(self._queues[queue_name])

        def lpush(self, queue_name, value):
            raise ValueError('Oh no!')

        def rpop(self, queue_name):
            try:
                return self._queues[queue_name].pop(-1)

            except IndexError:
                return None

    redis = MockRedis()

    def mock_redis(*args, **kwargs):
        return redis

    def mock_get_callable(module_name, callable_name):
        def process(*args, **kwargs):
            pass

        return process

    config_file = make_config_file({
        'queues': {'some-queue': {'handler': 'azafea.tests.test_cli'}},
    })

    with monkeypatch.context() as m:
        m.setattr(azafea.cli.commands, 'Redis', mock_redis)
        m.setattr(azafea.config, 'get_callable', mock_get_callable)

        with pytest.raises(azafea.cli.errors.UnknownErrorExit):
            azafea.cli.run_command('-c', str(config_file), 'replay-errors', 'some-queue')

    assert redis._queues == {
        'some-queue': [],
        'errors-some-queue': [b'event1', b'event2'],
    }

    capture = capfd.readouterr()
    assert 'Failed to push b\'event3\' back in "some-queue":' in capture.err


def test_refresh_views(capfd, make_config_file):
    config_file = make_config_file({
        'postgresql': {'database': 'azafea-tests'},
        'queues': {'metrics-3': {'handler': 'azafea.event_processors.endless.metrics.v3'}},
    })

    azafea.cli.run_command('-c', str(config_file), 'initdb')
    azafea.cli.run_command('-c', str(config_file), 'refresh-views')
    azafea.cli.run_command('-c', str(config_file), 'dropdb')


def test_refresh_views_no_view(capfd, make_config_file):
    config_file = make_config_file({'postgresql': {'database': 'azafea-tests'}})

    azafea.cli.run_command('-c', str(config_file), 'refresh-views')


def test_deploy_documentation(capfd):
    azafea.cli.run_command('deploy-documentation', '-t', '<token>', '-v', 'latest')
    capture = capfd.readouterr()
    assert 'Invalid token' in capture.err


def test_run(capfd, monkeypatch, make_config_file):
    class MockController:
        def __init__(self, config):
            pass

        def main(self):
            print('Running the mock controller…')

    def mock_get_callable(module_name, callable_name):
        def process(*args, **kwargs):
            pass

        return process

    config_file = make_config_file({'queues': {'some-queue': {'handler': 'azafea.tests.test_cli'}}})

    with monkeypatch.context() as m:
        m.setattr(azafea.config, 'get_callable', mock_get_callable)
        m.setattr(azafea.cli.commands, 'Controller', MockController)
        azafea.cli.run_command('-c', str(config_file), 'run')

    capture = capfd.readouterr()
    assert 'Running the mock controller…' in capture.out


def test_run_invalid_config(capfd, make_config_file):
    # Make a wrong config file
    config_file = make_config_file({'main': {'verbose': 'blah'}})

    with pytest.raises(azafea.cli.errors.InvalidConfigExit):
        azafea.cli.run_command('-c', str(config_file), 'run')

    capture = capfd.readouterr()
    assert "Invalid configuration:\n* main.verbose: 'blah' is not a boolean" in capture.err


def test_run_no_event_queue(capfd, make_config_file):
    # Make a wrong config file
    config_file = make_config_file({})

    with pytest.raises(azafea.cli.errors.NoEventQueueExit):
        azafea.cli.run_command('-c', str(config_file), 'run')

    capture = capfd.readouterr()
    assert 'Could not start: no event queue configured' in capture.err


def test_run_redis_connection_error(capfd, monkeypatch, make_config_file):
    def mock_get_callable(module_name, callable_name):
        def process(*args, **kwargs):
            pass

        return process

    # Hopefully nobody will ever run the tests with a Redis server accessible at this host:port
    config_file = make_config_file({
        'redis': {'host': 'no-such-host', 'port': 1},
        'queues': {'some-queue': {'handler': 'azafea.tests.test_cli'}}
    })

    with monkeypatch.context() as m:
        m.setattr(azafea.config, 'get_callable', mock_get_callable)

        with pytest.raises(azafea.cli.errors.ConnectionErrorExit):
            azafea.cli.run_command('-c', str(config_file), 'run')

    capture = capfd.readouterr()
    assert 'Could not connect to Redis:' in capture.err


def test_run_postgresql_connection_error(capfd, monkeypatch, make_config_file):
    class MockRedis:
        def __init__(self, *args, **kwargs):
            self.connection_pool = MockRedisConnectionPool()

    class MockRedisConnectionPool:
        def make_connection(self):
            return MockRedisConnection()

    class MockRedisConnection:
        def connect(self):
            pass

    def mock_get_callable(module_name, callable_name):
        def process(*args, **kwargs):
            pass

        return process

    # Hopefully nobody will ever run the tests with a Redis server accessible at this host:port
    config_file = make_config_file({
        'postgresql': {'host': 'no-such-host', 'port': 1},
        'queues': {'some-queue': {'handler': 'azafea.tests.test_cli'}}
    })

    with monkeypatch.context() as m:
        m.setattr(azafea.config, 'get_callable', mock_get_callable)
        m.setattr(azafea.processor, 'Redis', MockRedis)

        with pytest.raises(azafea.cli.errors.ConnectionErrorExit):
            azafea.cli.run_command('-c', str(config_file), 'run')

    capture = capfd.readouterr()
    assert ('Could not connect to PostgreSQL: connection refused on '
            'postgresql+psycopg2://azafea@no-such-host:1/azafea') in capture.err


def test_per_queue_command(capfd, monkeypatch, make_config_file):
    def mock_get_callable(module_name, callable_name):
        def process(*args, **kwargs):
            pass

        def register_commands(subs) -> None:
            do_something = subs.add_parser('do-something')
            do_something.set_defaults(subcommand=lambda *_: print('Doing something!'))

        assert callable_name in ('register_commands', 'process')

        if callable_name == 'register_commands':
            return register_commands

        if callable_name == 'process':
            return process

    config_file = make_config_file({
        'queues': {
            'some-queue': {
                'handler': 'azafea.tests.test_cli',
            },
        }
    })

    with monkeypatch.context() as m:
        m.setattr(azafea.config, 'get_callable', mock_get_callable)
        azafea.cli.run_command('-c', str(config_file), 'some-queue', 'do-something')

    capture = capfd.readouterr()
    assert 'Doing something!' in capture.out


def test_per_queue_invalid_command(capfd, monkeypatch, make_config_file):
    def mock_get_callable(module_name, callable_name):
        def process(*args, **kwargs):
            pass

        def register_commands(subs) -> None:
            do_something = subs.add_parser('do-something')
            do_something.set_defaults(subcommand=lambda *_: print('Doing something!'))

        assert callable_name in ('register_commands', 'process')

        if callable_name == 'register_commands':
            return register_commands

        if callable_name == 'process':
            return process

    config_file = make_config_file({
        'queues': {
            'some-queue': {
                'handler': 'azafea.tests.test_cli',
            },
        }
    })

    with monkeypatch.context() as m:
        m.setattr(azafea.config, 'get_callable', mock_get_callable)

        with pytest.raises(SystemExit):
            azafea.cli.run_command('-c', str(config_file), 'some-queue', 'initdb')

    capture = capfd.readouterr()
    assert "invalid choice: 'initdb' (choose from 'do-something')" in capture.err
