# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import argparse
from enum import IntEnum
import logging
from typing import List
import sys

from redis import Redis
from redis.exceptions import ConnectionError as RedisConnectionError

from .config import Config, InvalidConfigurationError
from .controller import Controller
from .logging import setup_logging
from .model import Db, PostgresqlConnectionError


log = logging.getLogger(__name__)


class ExitCode(IntEnum):
    OK = 0
    INVALID_CONFIG = -1
    NO_EVENT_QUEUE = -2
    CONNECTION_ERROR = -3
    UNKNOWN_ERROR = -4


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


def parse_args(args: List[str]) -> argparse.Namespace:
    parser = get_parser()

    return parser.parse_args(args)


def do_dropdb(args: argparse.Namespace) -> int:
    try:
        config = Config.from_file(args.config)

    except InvalidConfigurationError as e:
        print(str(e), file=sys.stderr)
        return ExitCode.INVALID_CONFIG

    setup_logging(verbose=config.main.verbose)
    config.warn_about_default_passwords()

    if not config.queues:
        log.error('Could not clear the database: no event queue configured')
        return ExitCode.NO_EVENT_QUEUE

    db = Db(config.postgresql.host, config.postgresql.port, config.postgresql.user,
            config.postgresql.password, config.postgresql.database)
    db.drop_all()

    return ExitCode.OK


def do_initdb(args: argparse.Namespace) -> int:
    try:
        config = Config.from_file(args.config)

    except InvalidConfigurationError as e:
        print(str(e), file=sys.stderr)
        return ExitCode.INVALID_CONFIG

    setup_logging(verbose=config.main.verbose)
    config.warn_about_default_passwords()

    if not config.queues:
        log.error('Could not initialize the database: no event queue configured')
        return ExitCode.NO_EVENT_QUEUE

    db = Db(config.postgresql.host, config.postgresql.port, config.postgresql.user,
            config.postgresql.password, config.postgresql.database)
    db.create_all()

    return ExitCode.OK


def do_print_config(args: argparse.Namespace) -> int:
    try:
        config = Config.from_file(args.config)

    except InvalidConfigurationError as e:
        print(str(e), file=sys.stderr)
        return ExitCode.INVALID_CONFIG

    setup_logging(verbose=config.main.verbose)
    config.warn_about_default_passwords()

    print(config)

    if not config.queues:
        log.warning('Did you forget to configure event queues?')
        return ExitCode.NO_EVENT_QUEUE

    return ExitCode.OK


def do_replay(args: argparse.Namespace) -> int:
    try:
        config = Config.from_file(args.config)

    except InvalidConfigurationError as e:
        print(str(e), file=sys.stderr)
        return ExitCode.INVALID_CONFIG

    setup_logging(verbose=config.main.verbose)
    config.warn_about_default_passwords()

    if not config.queues:
        log.error(f'Could not replay events from "{args.queue}": no event queue configured')
        return ExitCode.NO_EVENT_QUEUE

    if args.queue not in config.queues:
        log.error(f'Could not replay events from "{args.queue}": unknown event queue requested')
        return ExitCode.NO_EVENT_QUEUE

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

            return ExitCode.UNKNOWN_ERROR

    log.info(f'Successfully moved failed events back to "{args.queue}"')

    return ExitCode.OK


def do_run(args: argparse.Namespace) -> int:
    try:
        config = Config.from_file(args.config)

    except InvalidConfigurationError as e:
        print(str(e), file=sys.stderr)
        return ExitCode.INVALID_CONFIG

    setup_logging(verbose=config.main.verbose)
    config.warn_about_default_passwords()

    if not config.queues:
        log.error('Could not start: no event queue configured')
        return ExitCode.NO_EVENT_QUEUE

    controller = Controller(config)

    try:
        controller.main()

    except PostgresqlConnectionError as e:
        log.error('Could not connect to PostgreSQL: %s', e)
        return ExitCode.CONNECTION_ERROR

    except RedisConnectionError as e:
        log.error('Could not connect to Redis: %s', e)
        return ExitCode.CONNECTION_ERROR

    return ExitCode.OK
