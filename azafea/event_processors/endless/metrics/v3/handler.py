# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import logging

from sqlalchemy.exc import IntegrityError

from azafea.model import DbSession

from .model import new_aggregate_event, new_singular_event, parse_record


log = logging.getLogger(__name__)


def process(dbsession: DbSession, record: bytes) -> None:
    log.debug('Processing metric v3 record: %s', record)

    request_data = parse_record(record)

    for event_variant in request_data.singulars:
        singular_event = new_singular_event(event_variant, dbsession)

        if singular_event is not None:
            log.debug('Inserting singular metric:\n%s', singular_event)

    for event_variant in request_data.aggregates:
        aggregate_event = new_aggregate_event(event_variant, dbsession)
        log.debug('Inserting aggregate metric:\n%s', aggregate_event)

    try:
        dbsession.commit()

    except IntegrityError as e:
        # FIXME: This is fragile, can we do better?
        if "uq_metrics_request_v3_sha512" in str(e):
            log.debug('Request had already been processed in the past')
            return

        # FIXME: Given how the request is built, this shouldn't ever happen; if it does though, we
        # absolutely need an integration test
        raise  # pragma: no cover
