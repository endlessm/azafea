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

from ..events import UpdaterBranchSelected


log = logging.getLogger(__name__)


def register_commands(subs: argparse._SubParsersAction) -> None:
    normalize_vendors = subs.add_parser('normalize-vendors',
                                        help='Normalize the vendors in existing records')
    normalize_vendors.set_defaults(subcommand=do_normalize_vendors)


def _normalize_chunk(chunk: Query) -> None:
    for record in chunk:
        vendor = normalize_vendor(record.hardware_vendor)

        if vendor == record.hardware_vendor:
            continue

        record.hardware_vendor = vendor
        chunk.session.add(record)


def do_normalize_vendors(config: Config, args: argparse.Namespace) -> None:
    CHUNK_SIZE = 5000
    db = Db(config.postgresql.host, config.postgresql.port, config.postgresql.user,
            config.postgresql.password, config.postgresql.database)

    log.info('Normalizing the vendors for "updater branch selected" (%s) events',
             UpdaterBranchSelected.__event_uuid__)

    with db as dbsession:
        query = dbsession.chunked_query(UpdaterBranchSelected, chunk_size=CHUNK_SIZE)
        num_records = query.count()

        if num_records == 0:
            log.info('-> No "updater branch selected" record in database')
            return None

        for chunk_number, chunk in enumerate(query, start=1):
            _normalize_chunk(chunk)
            dbsession.commit()
            progress(chunk_number * CHUNK_SIZE, num_records)

    progress(num_records, num_records, end='\n')

    log.info('All done!')
