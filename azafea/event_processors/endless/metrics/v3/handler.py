# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import logging
from dataclasses import asdict
from datetime import datetime, timezone
from uuid import UUID

from azafea.model import DbSession
from sqlalchemy.exc import IntegrityError

from .model import (
    IGNORED_EVENTS,
    Channel,
    Request,
    new_aggregate_event,
    new_singular_event,
    parse_record,
)
from .utils import get_bytes


log = logging.getLogger(__name__)


def process(dbsession: DbSession, record: bytes) -> None:
    log.debug('Processing metric v3 record: %s', record)

    request_data, request_channel = parse_record(record)
    events_and_functions = (
        (request_data.singulars, new_singular_event),
        (request_data.aggregates, new_aggregate_event))
    channel_dict = asdict(request_channel)

    try:
        with dbsession.begin_nested():
            channel = Channel(**channel_dict)
            dbsession.add(channel)
    except IntegrityError:
        channel = dbsession.query(Channel).filter_by(**channel_dict).one()

    try:
        with dbsession.begin_nested():
            request = Request(
                sha512=request_data.sha512,  # type: ignore
                received_at=datetime.fromtimestamp(
                    request_data.received_at / 1000000, tz=timezone.utc
                ),
                absolute_timestamp=request_data.absolute_timestamp,
                relative_timestamp=request_data.relative_timestamp,
                channel=channel
            )
            dbsession.add(request)
    except Exception as e:
        log.error(e)

    for events, new_event in events_and_functions:
        for event_variant in events:
            event_id = str(UUID(bytes=get_bytes(event_variant.get_child_value(0))))
            if event_id in IGNORED_EVENTS:
                continue
            event = new_event(request_data, channel, event_id, event_variant, dbsession)

            if event is not None:
                dbsession.add(event)
                log.debug('Inserting metric:\n%s', event)
    dbsession.commit()
