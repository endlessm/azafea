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
from sqlalchemy.sql.functions import func

from azafea.config import Config
from azafea.model import Db
from azafea.utils import progress
from azafea.vendors import normalize_vendor

from ...image import parse_endless_os_image
from ..events import (
    ImageVersion,
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
    aggregate_event_is_known,
    sequence_is_known,
    singular_event_is_known,
)
from ..machine import Machine, insert_machine
from ..request import Request


log = logging.getLogger(__name__)


def register_commands(subs: argparse._SubParsersAction) -> None:
    dedupe_image_versions = subs.add_parser('dedupe-image-versions',
                                            help='Deduplicate the image version events',
                                            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    dedupe_image_versions.add_argument('--chunk-size', type=int, default=5000,
                                       help='The size of the chunks to operate on')
    dedupe_image_versions.set_defaults(subcommand=do_dedupe_image_versions)

    normalize_vendors = subs.add_parser('normalize-vendors',
                                        help='Normalize the vendors in existing records',
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    normalize_vendors.add_argument('--chunk-size', type=int, default=5000,
                                   help='The size of the chunks to operate on')
    normalize_vendors.set_defaults(subcommand=do_normalize_vendors)

    parse_images = subs.add_parser('parse-old-images',
                                   help='Parse the image ids in existing records',
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parse_images.add_argument('--chunk-size', type=int, default=5000,
                              help='The size of the chunks to operate on')
    parse_images.set_defaults(subcommand=do_parse_images)

    replay_machine_images = subs.add_parser('replay-machine-images',
                                            help='Replay "image version" events to populate the '
                                                 'machine mapping table',
                                            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    replay_machine_images.add_argument('--chunk-size', type=int, default=5000,
                                       help='The size of the chunks to operate on')
    replay_machine_images.set_defaults(subcommand=do_replay_machine_images)

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


def do_dedupe_image_versions(config: Config, args: argparse.Namespace) -> None:
    db = Db(config.postgresql)
    log.info('Deduplicating the metrics requests with multiple "image version" (%s) events',
             ImageVersion.__event_uuid__)

    with db as dbsession:
        query = dbsession.query(ImageVersion.request_id)
        query = query.group_by(ImageVersion.request_id)
        query = query.having(func.count(ImageVersion.id) > 1)
        num_requests_with_dupes = query.count()

        if num_requests_with_dupes == 0:
            log.info('-> No metrics requests with deduplicate image versions found')
            return None

        log.info('-> Found %s metrics requests with duplicate image versions',
                 num_requests_with_dupes)
        request_ids_with_dupes = [x[0] for x in query]

    previous_request_id = None

    for start in range(0, num_requests_with_dupes, args.chunk_size):
        stop = min(num_requests_with_dupes, start + args.chunk_size)
        request_id_chunk = request_ids_with_dupes[start:stop]

        with db as dbsession:
            query = dbsession.query(ImageVersion)
            query = query.filter(ImageVersion.request_id.in_(request_id_chunk))
            query = query.order_by(ImageVersion.request_id, ImageVersion.id)

            for image_version in query:
                if image_version.request_id == previous_request_id:
                    dbsession.delete(image_version)

                previous_request_id = image_version.request_id

        progress(stop, num_requests_with_dupes)

    progress(num_requests_with_dupes, num_requests_with_dupes, end='\n')
    log.info('All done!')


def _normalize_chunk(chunk: Query) -> None:
    for record in chunk:
        vendor = normalize_vendor(record.hardware_vendor)

        if vendor == record.hardware_vendor:
            continue

        record.hardware_vendor = vendor
        chunk.session.add(record)


def do_normalize_vendors(config: Config, args: argparse.Namespace) -> None:
    db = Db(config.postgresql)
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


def do_parse_images(config: Config, args: argparse.Namespace) -> None:
    db = Db(config.postgresql)
    log.info('Parsing the image ids for old activations')

    with db as dbsession:
        query = dbsession.chunked_query(Machine, chunk_size=args.chunk_size)
        query = query.filter(Machine.image_product.is_(None))
        query = query.reverse_chunks()
        num_records = query.count()

        if num_records == 0:
            log.info('-> No machine record with unparsed image ids')
            return None

        for chunk_number, chunk in enumerate(query, start=1):
            for machine in chunk:
                parsed_image = parse_endless_os_image(machine.image_id)

                for k, v in parsed_image.items():
                    setattr(machine, k, v)

            dbsession.commit()
            progress(chunk_number * args.chunk_size, num_records)

    progress(num_records, num_records, end='\n')

    log.info('All done!')


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

    log.info('Replaying the invalid sequences…')

    with db as dbsession:
        query = dbsession.chunked_query(InvalidSequence, chunk_size=args.chunk_size)
        query = query.reverse_chunks()
        total = query.count()

        for chunk_number, chunk in enumerate(query, start=1):
            replay_invalid_sequences(chunk)
            dbsession.commit()
            progress(chunk_number * args.chunk_size, total)

    progress(total, total, end='\n')


def do_replay_machine_images(config: Config, args: argparse.Namespace) -> None:
    db = Db(config.postgresql)
    log.info('Replaying the image version events…')

    with db as dbsession:
        query = dbsession.query(Request.machine_id, ImageVersion.image_id)
        query = query.filter(Request.id == ImageVersion.request_id)
        query = query.distinct()

        total = query.count()

        for i, (machine_id, image_id) in enumerate(query, start=1):
            insert_machine(dbsession, machine_id, image_id)

            if (i % args.chunk_size) == 0:
                dbsession.commit()
                progress(i, total)

        progress(total, total)


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

        # FIXME: Stop ignoring from coverage report once we actually have aggregate events
        for chunk_number, chunk in enumerate(query, start=1):  # pragma: no cover
            replay_unknown_aggregate_events(chunk)
            dbsession.commit()
            progress(chunk_number * args.chunk_size, total)

    progress(total, total, end='\n')

    log.info('Replaying the unknown sequences…')

    with db as dbsession:
        unknown_event_ids = dbsession.query(UnknownSequence.event_id).distinct()
        unknown_event_ids = (str(i[0]) for i in unknown_event_ids)
        unknown_event_ids = [i for i in unknown_event_ids if sequence_is_known(i)]

        query = dbsession.chunked_query(UnknownSequence, chunk_size=args.chunk_size)
        query = query.filter(UnknownSequence.event_id.in_(unknown_event_ids))
        query = query.reverse_chunks()
        total = query.count()

        for chunk_number, chunk in enumerate(query, start=1):
            replay_unknown_sequences(chunk)
            dbsession.commit()
            progress(chunk_number * args.chunk_size, total)

    progress(total, total, end='\n')
