# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import argparse
import logging

from redis import Redis
from redis.exceptions import ConnectionError as RedisConnectionError

from ..config import Config
from ..controller import Controller
from ..model import Db, PostgresqlConnectionError
from .errors import ConnectionErrorExit, NoEventQueueExit, UnknownErrorExit


log = logging.getLogger(__name__)


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='azafea',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-c', '--config', default='/etc/azafea/config.toml',
                        help='Optional path to a configuration file, if needed')

    subs = parser.add_subparsers(title='subcommands', dest='subcommand', required=True)

    dropdb = subs.add_parser('dropdb', help='Drop the tables in the database')
    dropdb.set_defaults(subcommand=do_dropdb)

    initdb = subs.add_parser('initdb', help='Initialize the database, creating the tables')
    initdb.set_defaults(subcommand=do_initdb)

    print_config = subs.add_parser('print-config',
                                   help='Print the loaded configuration then exit')
    print_config.set_defaults(subcommand=do_print_config)

    replay = subs.add_parser('replay-errors',
                             help='Pull events from the error queue and send them back to the '
                                  'incoming one')
    replay.add_argument('queue', help='The name of the queue to replay, e.g "ping-1"')
    replay.set_defaults(subcommand=do_replay)

    run = subs.add_parser('run', help='Run azafea')
    run.set_defaults(subcommand=do_run)

    return parser


def do_dropdb(config: Config, args: argparse.Namespace) -> None:
    if not config.queues:
        log.error('Could not clear the database: no event queue configured')
        raise NoEventQueueExit()

    db = Db(config.postgresql.host, config.postgresql.port, config.postgresql.user,
            config.postgresql.password, config.postgresql.database)
    db.drop_all()


def do_initdb(config: Config, args: argparse.Namespace) -> None:
    if not config.queues:
        log.error('Could not initialize the database: no event queue configured')
        raise NoEventQueueExit()

    db = Db(config.postgresql.host, config.postgresql.port, config.postgresql.user,
            config.postgresql.password, config.postgresql.database)
    db.create_all()


def do_print_config(config: Config, args: argparse.Namespace) -> None:
    print('----- BEGIN -----')
    print(config)
    print('------ END ------')

    if not config.queues:
        log.warning('Did you forget to configure event queues?')
        raise NoEventQueueExit()


def do_replay(config: Config, args: argparse.Namespace) -> None:
    if not config.queues:
        log.error(f'Could not replay events from "{args.queue}": no event queue configured')
        raise NoEventQueueExit()

    if args.queue not in config.queues:
        log.error(f'Could not replay events from "{args.queue}": unknown event queue requested')
        raise NoEventQueueExit()

    redis = Redis(host=config.redis.host, port=config.redis.port, password=config.redis.password)
    error_queue = f'errors-{args.queue}'

    # We could try and pull them out until there aren't any left, but we'd enter a race with Azafea:
    # if it pushes them back to the error queue faster than we pull from it, this command could
    # continue infinitely.
    #
    # Checking how many errors there are when we start and pulling only that mount means we lose the
    # new ones added while we pull, but then we can just rerun the command as needed.
    num_errors = redis.llen(error_queue)

    for i in range(num_errors):
        failed_event = redis.rpop(error_queue)

        if failed_event is None:
            log.warning(f'"{args.queue}" emptied faster than planned after {i} elements out of '
                        f'{num_errors}')
            break

        try:
            redis.lpush(args.queue, failed_event)

        except Exception:
            log.exception(f'Failed to push {failed_event} back in "{args.queue}":')
            raise UnknownErrorExit()

    log.info(f'Successfully moved failed events back to "{args.queue}"')


def do_run(config: Config, args: argparse.Namespace) -> None:
    if not config.queues:
        log.error('Could not start: no event queue configured')
        raise NoEventQueueExit()

    controller = Controller(config)

    try:
        controller.main()

    except PostgresqlConnectionError as e:
        log.error('Could not connect to PostgreSQL: %s', e)
        raise ConnectionErrorExit()

    except RedisConnectionError as e:
        log.error('Could not connect to Redis: %s', e)
        raise ConnectionErrorExit()
