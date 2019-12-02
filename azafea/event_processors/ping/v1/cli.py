# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import argparse
import logging

from sqlalchemy.orm.exc import NoResultFound

from azafea.config import Config
from azafea.model import Db, DbSession
from azafea.utils import progress
from azafea.vendors import normalize_vendor

from .handler import Ping, PingConfiguration


log = logging.getLogger(__name__)


def register_commands(subs: argparse._SubParsersAction) -> None:
    normalize_vendors = subs.add_parser('normalize-vendors',
                                        help='Normalize the vendors in existing records')
    normalize_vendors.set_defaults(subcommand=do_normalize_vendors)


def _normalize_chunk(dbsession: DbSession, start: int, stop: int) -> None:
    ping_configs = dbsession.query(PingConfiguration).order_by(PingConfiguration.id)
    pings = dbsession.query(Ping)

    for record in ping_configs.slice(start, stop):
        vendor = normalize_vendor(record.vendor)

        if vendor == record.vendor:
            continue

        try:
            # Is there already a ping config with the normalized vendor?
            existing = ping_configs.filter_by(image=record.image, product=record.product,
                                              dualboot=record.dualboot, vendor=vendor).one()

        except NoResultFound:
            # There isn't, so lets just normalize the vendor
            record.vendor = vendor
            dbsession.add(record)

            continue

        # There is, so we must move all the pings to that ping config…
        associated_pings = pings.filter_by(config_id=record.id)
        associated_pings.update({Ping.config_id: existing.id}, synchronize_session='fetch')

        assert pings.filter_by(config_id=record.id).count() == 0

        # … and delete the now unused ping configuration
        dbsession.delete(record)


def do_normalize_vendors(config: Config, args: argparse.Namespace) -> None:
    CHUNK_SIZE = 2000
    db = Db(config.postgresql.host, config.postgresql.port, config.postgresql.user,
            config.postgresql.password, config.postgresql.database)

    log.info('Normalizing the vendors for ping configurations')

    with db as dbsession:
        num_records = dbsession.query(PingConfiguration).count()

    if num_records == 0:
        log.info('-> No ping configuration record in database')
        return None

    for i in range(0, num_records, CHUNK_SIZE):
        stop = min(i + CHUNK_SIZE, num_records)

        with db as dbsession:
            _normalize_chunk(dbsession, i, stop)

        progress(stop, num_records)

    progress(num_records, num_records, end='\n')

    log.info('All done!')
