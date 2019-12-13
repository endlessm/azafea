# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import argparse
import logging

from sqlalchemy.orm.query import Query

from azafea.config import Config
from azafea.model import Db
from azafea.utils import progress
from azafea.vendors import normalize_vendor

from ..events import (
    InvalidAggregateEvent,
    InvalidSequence,
    InvalidSingularEvent,
    UnknownAggregateEvent,
    UnknownSequence,
    UnknownSingularEvent,
    UpdaterBranchSelected,
    replay_invalid_aggregate_events,
    replay_invalid_sequences,
    replay_invalid_singular_events,
    replay_unknown_aggregate_events,
    replay_unknown_sequences,
    replay_unknown_singular_events,
)


log = logging.getLogger(__name__)


def register_commands(subs: argparse._SubParsersAction) -> None:
    normalize_vendors = subs.add_parser('normalize-vendors',
                                        help='Normalize the vendors in existing records',
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    normalize_vendors.add_argument('--chunk-size', type=int, default=5000,
                                   help='The size of the chunks to operate on')
    normalize_vendors.set_defaults(subcommand=do_normalize_vendors)

    replay_invalid = subs.add_parser('replay-invalid', help='Replay invalid events',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    replay_invalid.add_argument('--chunk-size', type=int, default=5000,
                                help='The size of the chunks to operate on')
    replay_invalid.set_defaults(subcommand=do_replay_invalid)

    replay_unknown = subs.add_parser('replay-unknown', help='Replay unknown events',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    replay_unknown.add_argument('--chunk-size', type=int, default=5000,
                                help='The size of the chunks to operate on')
    replay_unknown.set_defaults(subcommand=do_replay_unknown)


def _normalize_chunk(chunk: Query) -> None:
    for record in chunk:
        vendor = normalize_vendor(record.hardware_vendor)

        if vendor == record.hardware_vendor:
            continue

        record.hardware_vendor = vendor
        chunk.session.add(record)


def do_normalize_vendors(config: Config, args: argparse.Namespace) -> None:
    db = Db(config.postgresql.host, config.postgresql.port, config.postgresql.user,
            config.postgresql.password, config.postgresql.database)

    log.info('Normalizing the vendors for "updater branch selected" (%s) events',
             UpdaterBranchSelected.__event_uuid__)

    with db as dbsession:
        query = dbsession.chunked_query(UpdaterBranchSelected, chunk_size=args.chunk_size)
        num_records = query.count()

        if num_records == 0:
            log.info('-> No "updater branch selected" record in database')
            return None

        for chunk_number, chunk in enumerate(query, start=1):
            _normalize_chunk(chunk)
            dbsession.commit()
            progress(chunk_number * args.chunk_size, num_records)

    progress(num_records, num_records, end='\n')

    log.info('All done!')


def do_replay_invalid(config: Config, args: argparse.Namespace) -> None:
    db = Db(config.postgresql.host, config.postgresql.port, config.postgresql.user,
            config.postgresql.password, config.postgresql.database)

    log.info('Replaying the invalid singular events…')

    with db as dbsession:
        query = dbsession.chunked_query(InvalidSingularEvent, chunk_size=args.chunk_size)
        total = query.count()

        for chunk_number, chunk in enumerate(query, start=1):
            replay_invalid_singular_events(chunk)
            dbsession.commit()
            progress(chunk_number * args.chunk_size, total)

    progress(total, total, end='\n')

    log.info('Replaying the invalid aggregate events…')

    with db as dbsession:
        query = dbsession.chunked_query(InvalidAggregateEvent, chunk_size=args.chunk_size)
        total = query.count()

        # FIXME: Stop ignoring from coverage report once we actually have aggregate events
        for chunk_number, chunk in enumerate(query, start=1):  # pragma: no cover
            replay_invalid_aggregate_events(chunk)
            dbsession.commit()
            progress(chunk_number * args.chunk_size, total)

    progress(total, total, end='\n')

    log.info('Replaying the invalid sequences…')

    with db as dbsession:
        query = dbsession.chunked_query(InvalidSequence, chunk_size=args.chunk_size)
        total = query.count()

        for chunk_number, chunk in enumerate(query, start=1):
            replay_invalid_sequences(chunk)
            dbsession.commit()
            progress(chunk_number * args.chunk_size, total)

    progress(total, total, end='\n')


def do_replay_unknown(config: Config, args: argparse.Namespace) -> None:
    db = Db(config.postgresql.host, config.postgresql.port, config.postgresql.user,
            config.postgresql.password, config.postgresql.database)

    log.info('Replaying the unknown singular events…')

    with db as dbsession:
        query = dbsession.chunked_query(UnknownSingularEvent, chunk_size=args.chunk_size)
        total = query.count()

        for chunk_number, chunk in enumerate(query, start=1):
            replay_unknown_singular_events(chunk)
            dbsession.commit()
            progress(chunk_number * args.chunk_size, total)

    progress(total, total, end='\n')

    log.info('Replaying the unknown aggregate events…')

    with db as dbsession:
        query = dbsession.chunked_query(UnknownAggregateEvent, chunk_size=args.chunk_size)
        total = query.count()

        # FIXME: Stop ignoring from coverage report once we actually have aggregate events
        for chunk_number, chunk in enumerate(query, start=1):  # pragma: no cover
            replay_unknown_aggregate_events(chunk)
            dbsession.commit()
            progress(chunk_number * args.chunk_size, total)

    progress(total, total, end='\n')

    log.info('Replaying the unknown sequences…')

    with db as dbsession:
        query = dbsession.chunked_query(UnknownSequence, chunk_size=args.chunk_size)
        total = query.count()

        for chunk_number, chunk in enumerate(query, start=1):
            replay_unknown_sequences(chunk)
            dbsession.commit()
            progress(chunk_number * args.chunk_size, total)

    progress(total, total, end='\n')
