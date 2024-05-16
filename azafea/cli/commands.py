# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import argparse
import logging

import requests
from alembic.command import revision as make_db_revision, upgrade as upgrade_db

from redis import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from sqlalchemy.exc import ProgrammingError

from ..config import Config
from ..controller import Controller
from ..migrations.utils import get_alembic_config, get_migration_heads, get_queue_migrations_path
from ..model import Db, PostgresqlConnectionError, views
from ..utils import progress
from .errors import ConnectionErrorExit, NoEventQueueExit, UnknownErrorExit


log = logging.getLogger(__name__)


def register_commands(subs: argparse._SubParsersAction) -> None:
    dropdb = subs.add_parser('dropdb', help='Drop the tables in the database')
    dropdb.set_defaults(subcommand=do_dropdb)

    initdb = subs.add_parser('initdb', help=argparse.SUPPRESS)
    initdb.set_defaults(subcommand=do_initdb)

    make_migration = subs.add_parser('make-migration', help='Generate a new database migration')
    make_migration.add_argument('-d', '--description', default='Automatically generated',
                                help='Description of the new migration')
    make_migration.add_argument('queue',
                                help='The name of the queue for which to generate the migration')
    make_migration.set_defaults(subcommand=do_make_migration)

    migratedb = subs.add_parser('migratedb', help='Migrate the database')
    migratedb.set_defaults(subcommand=do_migratedb)

    print_config = subs.add_parser('print-config',
                                   help='Print the loaded configuration then exit')
    print_config.set_defaults(subcommand=do_print_config)

    replay = subs.add_parser('replay-errors',
                             help='Pull events from the error queue and send them back to the '
                                  'incoming one')
    replay.add_argument('queue', help='The name of the queue to replay, e.g "ping-1"')
    replay.set_defaults(subcommand=do_replay)

    refresh = subs.add_parser('refresh-views',
                              help='Refresh the content of the materialized views')
    refresh.set_defaults(subcommand=do_refresh_views)

    deploy_documentation = subs.add_parser('deploy-documentation',
                                           help='Deploy documentation on ReadTheDocs')
    deploy_documentation.add_argument('-v', '--version', default='latest',
                                      help='Documentation version to deploy')
    deploy_documentation.add_argument('-t', '--token', help='ReadTheDocs token')
    deploy_documentation.set_defaults(subcommand=do_deploy_documentation)

    run = subs.add_parser('run', help='Run azafea')
    run.set_defaults(subcommand=do_run)


def do_dropdb(config: Config, args: argparse.Namespace) -> None:
    if not config.queues:
        log.error('Could not clear the database: no event queue configured')
        raise NoEventQueueExit()

    db = Db(config.postgresql)
    db.drop_all()


def do_initdb(config: Config, args: argparse.Namespace) -> None:
    if not config.queues:
        log.error('Could not initialize the database: no event queue configured')
        raise NoEventQueueExit()

    db = Db(config.postgresql)
    db.create_all()


def do_make_migration(config: Config, args: argparse.Namespace) -> None:
    if not config.queues:
        log.error(f'Could not generate a migration for "{args.queue}": no event queue configured')
        raise NoEventQueueExit()

    try:
        queue_handler = config.queues[args.queue].handler

    except KeyError:
        log.error(f'Could not generate a migration for "{args.queue}": unknown event queue '
                  'requested')
        raise NoEventQueueExit()

    alembic_config = get_alembic_config(config)

    if not alembic_config.get_main_option('version_locations'):
        log.info("Configured queue handlers don't have 'migrations' directories")
        return None

    db = Db(config.postgresql)

    with db as dbsession:
        alembic_config.attributes['connection'] = dbsession.connection()

        for h in get_migration_heads(alembic_config):
            if h.branch_labels is not None and args.queue in h.branch_labels:  # pragma: no branch
                # This queue already had migrations
                branch_label = None
                head = f'{args.queue}@head'
                break

        else:
            # This would be the first migration for this queue
            branch_label = args.queue
            head = 'base'

        make_db_revision(alembic_config, message=args.description, autogenerate=True,
                         version_path=get_queue_migrations_path(queue_handler),
                         branch_label=branch_label, head=head)


def do_migratedb(config: Config, args: argparse.Namespace) -> None:
    if not config.queues:
        log.error('Could not migrate the database: no event queue configured')
        raise NoEventQueueExit()

    alembic_config = get_alembic_config(config)

    if not alembic_config.get_main_option('version_locations'):
        log.info("Configured queue handlers don't have migrations")
        return None

    db = Db(config.postgresql)

    with db as dbsession:
        alembic_config.attributes['connection'] = dbsession.connection()
        upgrade_db(alembic_config, 'heads')

    log.info('Successfully migrated the database')


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

    redis = Redis(
        host=config.redis.host,
        port=config.redis.port,
        password=config.redis.password,
        ssl=config.redis.ssl,
    )
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


def do_refresh_views(config: Config, args: argparse.Namespace) -> None:
    db = Db(config.postgresql)
    total_nb_views = nb_views = len(views)
    log.info(f'Refreshing {nb_views} materialized views')

    with db as dbsession:
        for i, view in enumerate(views):
            progress(i, nb_views)
            try:
                dbsession.connection().execute(f'REFRESH MATERIALIZED VIEW "{view}"')
            except ProgrammingError as e:
                assert 'UndefinedTable' in str(e)
                log.debug(f'View {view} has not been created')
                total_nb_views -= 1

    progress(total_nb_views, total_nb_views, end='\n')
    log.info(f'Successfully refreshed {total_nb_views} materialized views')


def do_deploy_documentation(config: Config, args: argparse.Namespace) -> None:
    log.info('Deploying documentation on ReadTheDocs')
    url = f'https://readthedocs.org/api/v3/projects/azafea/versions/{args.version}/builds/'
    response = requests.post(url, headers={'Authorization': f'token {args.token}'})
    if response.ok:  # pragma: no cover
        log.info('Documentation deployment successfully triggered on ReadTheDocs')
    else:
        log.error('Could not deploy documentation on ReadTheDocs: %s',
                  response.json().get('detail', '(No reason)'))


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
