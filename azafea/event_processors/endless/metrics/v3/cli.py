# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import argparse
import logging

from azafea.config import Config
from azafea.model import Db
from azafea.utils import progress

from .model import (
    InvalidAggregateEvent,
    InvalidSingularEvent,
    UnknownAggregateEvent,
    UnknownSingularEvent,
    aggregate_event_is_known,
    replay_invalid_aggregate_events,
    replay_invalid_singular_events,
    replay_unknown_aggregate_events,
    replay_unknown_singular_events,
    singular_event_is_known,
)


log = logging.getLogger(__name__)


def register_commands(subs: argparse._SubParsersAction) -> None:
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


def do_replay_invalid(config: Config, args: argparse.Namespace) -> None:
    db = Db(config.postgresql)
    log.info('Replaying the invalid singular events…')

    with db as dbsession:
        query = dbsession.chunked_query(InvalidSingularEvent, chunk_size=args.chunk_size)
        query = query.reverse_chunks()
        total = query.count()

        for chunk_number, chunk in enumerate(query, start=1):
            replay_invalid_singular_events(chunk)
            dbsession.commit()
            progress(chunk_number * args.chunk_size, total)

    progress(total, total, end='\n')

    log.info('Replaying the invalid aggregate events…')

    with db as dbsession:
        query = dbsession.chunked_query(InvalidAggregateEvent, chunk_size=args.chunk_size)
        query = query.reverse_chunks()
        total = query.count()

        # FIXME: Stop ignoring from coverage report once we actually have aggregate events
        for chunk_number, chunk in enumerate(query, start=1):  # pragma: no cover
            replay_invalid_aggregate_events(chunk)
            dbsession.commit()
            progress(chunk_number * args.chunk_size, total)

    progress(total, total, end='\n')


def do_replay_unknown(config: Config, args: argparse.Namespace) -> None:
    db = Db(config.postgresql)
    log.info('Replaying the unknown singular events…')

    with db as dbsession:
        unknown_event_ids = dbsession.query(UnknownSingularEvent.event_id).distinct()
        unknown_event_ids = (str(i[0]) for i in unknown_event_ids)
        unknown_event_ids = [i for i in unknown_event_ids if singular_event_is_known(i)]

        query = dbsession.chunked_query(UnknownSingularEvent, chunk_size=args.chunk_size)
        query = query.filter(UnknownSingularEvent.event_id.in_(unknown_event_ids))
        query = query.reverse_chunks()
        total = query.count()

        progress(0, total)
        for chunk_number, chunk in enumerate(query, start=1):
            replay_unknown_singular_events(chunk)
            dbsession.commit()
            progress(chunk_number * args.chunk_size, total)

    progress(total, total, end='\n')

    log.info('Replaying the unknown aggregate events…')

    with db as dbsession:
        unknown_event_ids = dbsession.query(UnknownAggregateEvent.event_id).distinct()
        unknown_event_ids = (str(i[0]) for i in unknown_event_ids)
        unknown_event_ids = [i for i in unknown_event_ids if aggregate_event_is_known(i)]

        query = dbsession.chunked_query(UnknownAggregateEvent, chunk_size=args.chunk_size)
        query = query.filter(UnknownAggregateEvent.event_id.in_(unknown_event_ids))
        query = query.reverse_chunks()
        total = query.count()

        progress(0, total)
        # FIXME: Stop ignoring from coverage report once we actually have aggregate events
        for chunk_number, chunk in enumerate(query, start=1):  # pragma: no cover
            replay_unknown_aggregate_events(chunk)
            dbsession.commit()
            progress(chunk_number * args.chunk_size, total)

    progress(total, total, end='\n')
