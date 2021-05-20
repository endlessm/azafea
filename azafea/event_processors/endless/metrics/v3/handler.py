# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import logging
from uuid import UUID

from azafea.model import DbSession

from .model import IGNORED_EVENTS, new_aggregate_event, new_singular_event, parse_record
from .utils import get_bytes


log = logging.getLogger(__name__)


def process(dbsession: DbSession, record: bytes) -> None:
    log.debug('Processing metric v3 record: %s', record)

    request = parse_record(record)
    events_and_functions = (
        (request.singulars, new_singular_event),
        (request.aggregates, new_aggregate_event))

    for events, new_event in events_and_functions:
        for event_variant in events:
            event_id = str(UUID(bytes=get_bytes(event_variant.get_child_value(0))))
            if event_id in IGNORED_EVENTS:
                continue
            event = new_event(request, event_id, event_variant, dbsession)
            if event is not None:
                dbsession.add(event)
                log.debug('Inserting metric:\n%s', event)

    dbsession.commit()
