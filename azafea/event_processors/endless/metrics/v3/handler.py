# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import logging
from dataclasses import asdict
from uuid import UUID

from azafea.model import DbSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from .model import (
    IGNORED_EVENTS, Channel, Request, new_aggregate_event, new_singular_event, parse_record
)
from .utils import get_bytes


log = logging.getLogger(__name__)


def process(dbsession: DbSession, record: bytes) -> None:
    log.debug('Processing metric v3 record: %s', record)

    request, request_channel = parse_record(record)
    events_and_functions = (
        (request.singulars, new_singular_event),
        (request.aggregates, new_aggregate_event))
    channel_dict = asdict(request_channel)
    try:
        dbsession.add(Request(sha512=request.sha512))
        dbsession.commit()
    except IntegrityError:
        log.debug('Request had already been processed in the past')
        return
    try:
        channel = dbsession.query(Channel).filter_by(**channel_dict).one()
    except NoResultFound:
        try:
            with dbsession.begin_nested():
                channel = Channel(**channel_dict)
                dbsession.add(channel)
        except IntegrityError:
            channel = dbsession.query(Channel).filter_by(**channel_dict).one()

    for events, new_event in events_and_functions:
        for event_variant in events:
            event_id = str(UUID(bytes=get_bytes(event_variant.get_child_value(0))))
            if event_id in IGNORED_EVENTS:
                continue
            event = new_event(request, channel, event_id, event_variant, dbsession)

            if event is not None:
                dbsession.add(event)
                log.debug('Inserting metric:\n%s', event)
    dbsession.commit()
