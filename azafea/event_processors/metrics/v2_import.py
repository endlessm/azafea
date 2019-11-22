# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import logging

from sqlalchemy.orm.session import Session as DbSession

from .v2.handler import do_process


log = logging.getLogger(__name__)


# FIXME: Remove this once the import is successful
def process(dbsession: DbSession, record: bytes) -> None:
    log.debug('Importing metric v2 record: %s', record)

    do_process(dbsession, record, discard_serialized=True)
