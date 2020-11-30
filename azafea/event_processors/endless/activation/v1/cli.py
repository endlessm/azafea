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

from ...image import parse_endless_os_image
from .handler import Activation


log = logging.getLogger(__name__)


def register_commands(subs: argparse._SubParsersAction) -> None:
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


def _normalize_chunk(chunk: Query) -> None:
    for record in chunk:
        vendor = normalize_vendor(record.vendor)

        if vendor == record.vendor:
            continue

        record.vendor = vendor
        chunk.session.add(record)


def do_normalize_vendors(config: Config, args: argparse.Namespace) -> None:
    db = Db(config.postgresql)
    log.info('Normalizing the vendors for activations')

    with db as dbsession:
        query = dbsession.chunked_query(Activation, chunk_size=args.chunk_size)
        num_records = query.count()

        if num_records == 0:
            log.info('-> No activation record in database')
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
        query = dbsession.chunked_query(Activation, chunk_size=args.chunk_size)
        query = query.filter(Activation.image_product.is_(None))
        query = query.filter(Activation.image != 'unknown')
        query = query.reverse_chunks()
        num_records = query.count()

        if num_records == 0:
            log.info('-> No activation record with unparsed image ids')
            return None

        for chunk_number, chunk in enumerate(query, start=1):
            for activation in chunk:
                parsed_image = parse_endless_os_image(activation.image)

                for k, v in parsed_image.items():
                    setattr(activation, k, v)

            dbsession.commit()
            progress(chunk_number * args.chunk_size, num_records)

    progress(num_records, num_records, end='\n')

    log.info('All done!')
