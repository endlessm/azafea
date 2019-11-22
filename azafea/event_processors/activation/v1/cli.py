# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import argparse
import logging

from sqlalchemy.orm.session import Session as DbSession

from azafea.config import Config
from azafea.model import Db
from azafea.utils import progress
from azafea.vendors import normalize_vendor

from .handler import Activation


log = logging.getLogger(__name__)


def register_commands(subs: argparse._SubParsersAction) -> None:
    normalize_vendors = subs.add_parser('normalize-vendors',
                                        help='Normalize the vendors in existing records')
    normalize_vendors.set_defaults(subcommand=do_normalize_vendors)


def _normalize_chunk(dbsession: DbSession, start: int, stop: int) -> None:
    records = dbsession.query(Activation).order_by(Activation.id)

    for record in records.slice(start, stop):
        vendor = normalize_vendor(record.vendor)

        if vendor == record.vendor:
            continue

        record.vendor = vendor
        dbsession.add(record)


def do_normalize_vendors(config: Config, args: argparse.Namespace) -> None:
    CHUNK_SIZE = 5000
    db = Db(config.postgresql.host, config.postgresql.port, config.postgresql.user,
            config.postgresql.password, config.postgresql.database)

    log.info('Normalizing the vendors for activations')

    with db as dbsession:
        num_records = dbsession.query(Activation).count()

    if num_records == 0:
        log.info('-> No activation record in database')
        return None

    for i in range(0, num_records, CHUNK_SIZE):
        stop = min(i + CHUNK_SIZE, num_records)

        with db as dbsession:
            _normalize_chunk(dbsession, i, stop)

        progress(stop, num_records)

    progress(num_records, num_records, end='\n')

    log.info('All done!')
