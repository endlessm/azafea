# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session as DbSession

from .events import new_singular_event
from .request import RequestBuilder


log = logging.getLogger(__name__)


def process(dbsession: DbSession, record: bytes) -> None:
    log.debug('Processing metric v2 record: %s', record)

    request_builder = RequestBuilder.parse_bytes(record)
    request = request_builder.build_request()
    dbsession.add(request)

    try:
        dbsession.commit()

    except IntegrityError as e:
        # FIXME: This is fragile, can we do better?
        if "uq_metrics_request_v2_sha512" in str(e):
            log.debug('Request had already been processed in the past')
            return

        # FIXME: Given how the request is built, this shouldn't ever happen; if it does though, we
        # absolutely need an integration test
        raise  # pragma: no cover

    for event_variant in request_builder.singulars:
        singular_event = new_singular_event(request, event_variant, dbsession)
        log.debug('Inserting singular metric:\n%s', singular_event)

    # TODO: Handle aggregate events
    # TODO: Handle sequence events
